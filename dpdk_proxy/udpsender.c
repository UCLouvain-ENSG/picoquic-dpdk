/* SPDX-License-Identifier: BSD-3-Clause
 * Copyright(c) 2010-2014 Intel Corporation
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <sys/queue.h>
#include <netinet/if_ether.h>

#include <stdint.h>
#include <sys/queue.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>
#include <errno.h>
#include <signal.h>
#include <stdarg.h>
#include <inttypes.h>
#include <getopt.h>
#include <termios.h>
#include <unistd.h>
#include <pthread.h>

#include <rte_common.h>
#include <rte_log.h>
#include <rte_malloc.h>
#include <rte_memory.h>
#include <rte_memcpy.h>
#include <rte_eal.h>
#include <rte_launch.h>
#include <rte_atomic.h>
#include <rte_cycles.h>
#include <rte_prefetch.h>
#include <rte_lcore.h>
#include <rte_per_lcore.h>
#include <rte_branch_prediction.h>
#include <rte_interrupts.h>
#include <rte_random.h>
#include <rte_debug.h>
#include <rte_ether.h>
#include <rte_ethdev.h>
#include <rte_mempool.h>
#include <rte_mbuf.h>
#include <rte_string_fns.h>
#include <rte_ip.h>
#include <rte_tcp.h>
#include <rte_arp.h>
#include <rte_spinlock.h>
#include <rte_devargs.h>
#include <rte_version.h>

#include "token_bucket.h"

#define MAX_PKT_BURST 32
#define MEMPOOL_CACHE_SIZE 256
#define RTE_TEST_RX_DESC_DEFAULT 1024
#define RTE_TEST_TX_DESC_DEFAULT 1024
uint32_t tx_ip_src_addr = (4U << 24) | (18 << 16) | (0 << 8) | 1;
uint32_t tx_ip_dst_addr = (4U << 24) | (18 << 16) | (0 << 8) | 2;

uint16_t tx_udp_src_port = 87;
uint16_t tx_udp_dst_port = 87;

#define IP_DEFTTL 64
struct rte_mempool *mb_pool;

static uint16_t nb_rxd = RTE_TEST_RX_DESC_DEFAULT;
static uint16_t nb_txd = RTE_TEST_TX_DESC_DEFAULT;
static struct rte_ether_addr eth_addr;
static struct rte_ether_addr eth_addr_peer;
struct token_bucket tb;
int actual_size;
int test_duration;
uint64_t rate;
uint64_t multiplier;

static struct rte_eth_conf port_conf = {
    .rxmode = {
        .split_hdr_size = 0,
    },
    .txmode = {
        .mq_mode = ETH_MQ_TX_NONE,
    },
};


int str_to_mac(char *mac_txt, struct rte_ether_addr *mac_addr)
{
    int values[6];
    int i;
    if (6 == sscanf(mac_txt, "%x:%x:%x:%x:%x:%x%*c",
                    &values[0], &values[1], &values[2],
                    &values[3], &values[4], &values[5]))
    {
        /* convert to uint8_t */
        for (i = 0; i < 6; ++i){
            (mac_addr -> addr_bytes)[i] = (uint8_t)values[i];
        }
        return 0;
    }

    else
    {
        printf("invalid mac address : %s\n",mac_txt);
        return -1;
    }
}
void setup_pkt_udp_ip_headers(struct rte_ipv4_hdr *ip_hdr,
                              struct rte_udp_hdr *udp_hdr,
                              uint16_t pkt_data_len)
{
    uint16_t *ptr16;
    uint32_t ip_cksum;
    uint16_t pkt_len;

    /*
     * Initialize UDP header.
     */
    pkt_len = (uint16_t)(pkt_data_len + sizeof(struct rte_udp_hdr));
    udp_hdr->src_port = rte_cpu_to_be_16(tx_udp_src_port);
    udp_hdr->dst_port = rte_cpu_to_be_16(tx_udp_dst_port);
    udp_hdr->dgram_len = rte_cpu_to_be_16(pkt_len);
    udp_hdr->dgram_cksum = 0; /* No UDP checksum. */

    /*
     * Initialize IP header.
     */
    pkt_len = (uint16_t)(pkt_len + sizeof(struct rte_ipv4_hdr));
    ip_hdr->version_ihl = RTE_IPV4_VHL_DEF;
    ip_hdr->type_of_service = 0;
    ip_hdr->fragment_offset = 0;
    ip_hdr->time_to_live = IP_DEFTTL;
    ip_hdr->next_proto_id = IPPROTO_UDP;
    ip_hdr->packet_id = 0;
    ip_hdr->total_length = rte_cpu_to_be_16(pkt_len);
    ip_hdr->src_addr = rte_cpu_to_be_32(tx_ip_src_addr);
    ip_hdr->dst_addr = rte_cpu_to_be_32(tx_ip_dst_addr);

    /*
     * Compute IP header checksum.
     */
    ptr16 = (unaligned_uint16_t *)ip_hdr;
    ip_cksum = 0;
    ip_cksum += ptr16[0];
    ip_cksum += ptr16[1];
    ip_cksum += ptr16[2];
    ip_cksum += ptr16[3];
    ip_cksum += ptr16[4];
    ip_cksum += ptr16[6];
    ip_cksum += ptr16[7];
    ip_cksum += ptr16[8];
    ip_cksum += ptr16[9];

    /*
     * Reduce 32 bit checksum to 16 bits and complement it.
     */
    ip_cksum = ((ip_cksum & 0xFFFF0000) >> 16) +
               (ip_cksum & 0x0000FFFF);
    if (ip_cksum > 65535)
        ip_cksum -= 65535;
    ip_cksum = (~ip_cksum) & 0x0000FFFF;
    if (ip_cksum == 0)
        ip_cksum = 0xFFFF;
    ip_hdr->hdr_checksum = (uint16_t)ip_cksum;
}

void copy_buf_to_pkt_segs(void *buf, unsigned len, struct rte_mbuf *pkt,
                          unsigned offset)
{
    struct rte_mbuf *seg;
    void *seg_buf;
    unsigned copy_len;

    seg = pkt;
    while (offset >= seg->data_len)
    {
        offset -= seg->data_len;
        seg = seg->next;
    }
    copy_len = seg->data_len - offset;
    seg_buf = rte_pktmbuf_mtod_offset(seg, char *, offset);
    while (len > copy_len)
    {
        rte_memcpy(seg_buf, buf, (size_t)copy_len);
        len -= copy_len;
        buf = ((char *)buf + copy_len);
        seg = seg->next;
        seg_buf = rte_pktmbuf_mtod(seg, char *);
        copy_len = seg->data_len;
    }
    rte_memcpy(seg_buf, buf, (size_t)len);
}

void copy_buf_to_pkt(void *buf, unsigned len, struct rte_mbuf *pkt, unsigned offset)
{

    rte_memcpy(rte_pktmbuf_mtod_offset(pkt, char *, offset),
               buf, (size_t)len);
    return;
}

void my_sleeper(int it){
    int size = 10000;
    char *dummy = malloc(size);
    for(int i = 0; i < it; i++){
        memset(dummy,0,size);
    }
    free(dummy);
}
static int
lcore_hello(__rte_unused void *arg)
{
    uint16_t portid = 0;
    int ret;
    struct rte_eth_rxconf rxq_conf;
    struct rte_eth_txconf txq_conf;
    struct rte_eth_dev_info dev_info;
    struct rte_eth_dev_tx_buffer *tx_buffer;
    struct rte_mbuf *m;
    struct rte_eth_conf local_port_conf = port_conf;
    struct rte_ether_hdr *eth;
    void *tmp;

    tx_buffer = rte_zmalloc_socket("tx_buffer",
                                   RTE_ETH_TX_BUFFER_SIZE(MAX_PKT_BURST), 0,
                                   rte_eth_dev_socket_id(0));
    if (tx_buffer == NULL)
    {
        printf("fail to init buffer\n");
        return 0;
    }

    if (mb_pool == NULL)
    {
        printf("fail to init mb_pool\n");
        return 0;
    }
    ret = rte_eth_dev_info_get(0, &dev_info);
    if (ret != 0)
        rte_exit(EXIT_FAILURE,
                 "Error during getting device (port %u) info: %s\n",
                 0, strerror(-ret));

    if (dev_info.tx_offload_capa & DEV_TX_OFFLOAD_MBUF_FAST_FREE)
        local_port_conf.txmode.offloads |=
            DEV_TX_OFFLOAD_MBUF_FAST_FREE;
    ret = rte_eth_dev_configure(0, 1, 1, &local_port_conf);
    if (ret != 0)
    {
        printf("error in dev_configure\n");
        return 0;
    }

    ret = rte_eth_dev_adjust_nb_rx_tx_desc(portid, &nb_rxd,
                                           &nb_txd);
    if (ret < 0)
        rte_exit(EXIT_FAILURE,
                 "Cannot adjust number of descriptors: err=%d, port=%u\n",
                 ret, portid);

    ret = rte_eth_macaddr_get(portid, &eth_addr);

    // init tx queue
    txq_conf = dev_info.default_txconf;
    txq_conf.offloads = local_port_conf.txmode.offloads;
    ret = rte_eth_tx_queue_setup(portid, 0, nb_txd,
                                 rte_eth_dev_socket_id(portid),
                                 &txq_conf);
    if (ret != 0)
    {
        printf("failed to init queue\n");
        return 0;
    }

    // init rx queue
    rxq_conf = dev_info.default_rxconf;
    rxq_conf.offloads = local_port_conf.rxmode.offloads;
    ret = rte_eth_rx_queue_setup(0, 0, nb_rxd, rte_eth_dev_socket_id(0), &rxq_conf, mb_pool);
    if (ret != 0)
    {
        printf("failed to init rx_queue\n");
    }

    

    printf("before start \n");
    ret = rte_eth_dev_start(0);
    if (ret != 0)
    {
        printf("failed to start device\n");
    }

    size_t pkt_size;
    m = rte_pktmbuf_alloc(mb_pool);
    if (m == NULL)
    // printf("hello\n");
    {
        printf("fail to init pktmbuf\n");
        return 0;
    }

    struct rte_ipv4_hdr ip_hdr;
    struct rte_udp_hdr rte_udp_hdr;
    struct rte_ether_hdr *eth_hdr;

    char udp_payload[1200];
    uint32_t my_counter = 0;
    memset(udp_payload,0,1200);
    struct timeval start_time;
    struct timeval current_time;
    double slow_start_delay = 15;
    int slow_start_finished = 0;
    struct timeval timer_increasing_tp_start;
    struct timeval timer_increasing_tp_finish;
    int fast_increasing = 0;
    
	gettimeofday(&start_time, NULL);
    uint64_t packet_counter = 0;
    //for(int i = 0; i<1000000;i++)
    uint32_t pacing_counter = 0;
    while (1)
    {
        gettimeofday(&current_time, NULL);        
        double elapsed = 0.0;
		elapsed = (current_time.tv_sec*1000 - start_time.tv_sec*1000) + (current_time.tv_usec/1000 - start_time.tv_usec/1000);
        if(elapsed > 1000){
            u_int64_t new_rate = rate + ((uint64_t) (100*1000)) *multiplier;
            configure_token_bucket(&tb, new_rate, ((u_int64_t ) 4) * new_rate);
            rate = new_rate;
            gettimeofday(&start_time, NULL);
        }
       

        wait_until_token_available(&tb, (uint64_t)actual_size*8*16);
        for(int i = 0; i < 16; i++){

            int offset = 0;
            memcpy(udp_payload,&my_counter,4);
            my_counter++;
            m = rte_pktmbuf_alloc(mb_pool);
            
            if (m == NULL)
            {
                printf("fail to init pktmbuf\n");
                rte_exit(EXIT_FAILURE, "%s\n", rte_strerror(rte_errno));
                return 0;
            }
            eth_hdr = rte_pktmbuf_mtod(m, struct rte_ether_hdr *);

            eth_hdr -> ether_type = rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4);
#if RTE_VERSION < RTE_VERSION_NUM(21,11,0,0)
            rte_ether_addr_copy(&eth_addr, &eth_hdr->s_addr);
            rte_ether_addr_copy(&eth_addr_peer, &eth_hdr->d_addr);
#else
            rte_ether_addr_copy(&eth_addr, &eth_hdr->src_addr);
            rte_ether_addr_copy(&eth_addr_peer, &eth_hdr->dst_addr);
#endif
            setup_pkt_udp_ip_headers(&ip_hdr, &rte_udp_hdr, actual_size);
            copy_buf_to_pkt(eth_hdr, sizeof(struct rte_ether_hdr), m, offset);
            offset += sizeof(struct rte_ether_hdr);
            copy_buf_to_pkt(&ip_hdr, sizeof(struct rte_ipv4_hdr), m, offset);
            offset += sizeof(struct rte_ipv4_hdr);
            copy_buf_to_pkt(&rte_udp_hdr, sizeof(struct rte_udp_hdr), m, offset);
            offset += sizeof(struct rte_udp_hdr);
            copy_buf_to_pkt(udp_payload, actual_size, m, offset);
            offset += actual_size;

            // inchallah ca marche
            // printf("offset : %d\n",offset);
            // printf("rte_eth_hdr : %d\n",sizeof(struct rte_ether_hdr));
            // printf("length : %d\n",htons(ip_hdr.total_length));
            m->data_len = offset;
            m->pkt_len = offset;


            //printf("offset : %d\n",offset);
            
            int sent = rte_eth_tx_burst(0, 0, &m,1);
        }
        // struct timespec request = {0, 10000};
        // nanosleep(&request, NULL);


        packet_counter += 16;
        struct rte_ipv4_hdr *ip_hdr2;
        ip_hdr2 = (struct rte_ipv4_hdr *)(rte_pktmbuf_mtod(m, char *) + sizeof(struct rte_ether_hdr));

        struct rte_udp_hdr *udp2 = (struct rte_udp_hdr *)((unsigned char *)ip_hdr2 +
                                                        sizeof(struct rte_ipv4_hdr));
        unsigned char *payload2 = (unsigned char *)(udp2 + 1);
        uint32_t msg;
        memcpy(&msg,payload2,4);
        if(msg != (my_counter -1)){
                printf("loss detected at packet real dumb %u\n",my_counter);
                printf("expected : %u\n",my_counter);
                printf("actual : %u\n",my_counter);
                printf("packet lost\n");
                my_counter = msg + 1;
        }
        
        // if(packet_counter % 1000 == 0){
        //     printf("packet_counter: %d\n",packet_counter);
        // }
    }
    printf("nb_packet_transmitted : %lu\n",packet_counter);

}

int main(int argc, char **argv)
{

    int ret;
    ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_panic("Cannot init EAL\n");
    argc -= ret;
        argv += ret;
    unsigned int nb_mbufs = RTE_MAX(1 * (1 + 1 + MAX_PKT_BURST + 2 * MEMPOOL_CACHE_SIZE), 8192U);
    mb_pool = rte_pktmbuf_pool_create("mbuf_pool", nb_mbufs,
                                      MEMPOOL_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE,
                                      rte_socket_id());


    str_to_mac(argv[1],&eth_addr_peer);
    printf("==================argc : %d\n",argc);
    
    actual_size = atoi(argv[2]);
    multiplier = (uint64_t) atoi(argv[3]);
    printf("payload size : %d\n",actual_size);
    printf("rate multiplier : %ld\n",multiplier);
    rate = 100*1000;
    init_token_bucket(&tb, rate, ((u_int64_t ) 4) * rate);

    unsigned lcore_id;
    /* call lcore_hello() on every worker lcore */
    RTE_LCORE_FOREACH_WORKER(lcore_id)
    {
    	rte_eal_remote_launch(lcore_hello, NULL, lcore_id);
    }

    /* call it on main lcore too */
    // lcore_hello(NULL);
    rte_eal_mp_wait_lcore();

    /* clean up the EAL */
    rte_eal_cleanup();

    return 0;
}
