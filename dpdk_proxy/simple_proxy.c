/* SPDX-License-Identifier: BSD-3-Clause
 * Copyright(c) 2010-2014 Intel Corporation
 */



// Simple proxy that listens to two ports and forwards packets from one port to another

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

#define MAX_PKT_BURST 32
#define MEMPOOL_CACHE_SIZE 256
#define RTE_TEST_RX_DESC_DEFAULT 1024
#define RTE_TEST_TX_DESC_DEFAULT 1024
#define IP_DEFTTL 64
struct rte_eth_rxconf rxq_conf;
struct rte_eth_txconf txq_conf;

const int NB_OF_PORTS = 1;
struct rte_mempool *mb_pool;
struct rte_eth_dev_tx_buffer *tx_buffer;
struct rte_ether_addr peer_addresses[2];

static uint16_t nb_rxd = RTE_TEST_RX_DESC_DEFAULT;
static uint16_t nb_txd = RTE_TEST_TX_DESC_DEFAULT;
struct rte_mbuf *pkts_burst[MAX_PKT_BURST];

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



int dpdk_init_mbuf_txbuffer(uint16_t portid)
{

    char mbuf_pool_name[20] = "mbuf_pool_X";
    char tx_buffer_name[20] = "tx_buffer_X";
    int index_of_X;
    char char_i = portid;
    index_of_X = strlen(mbuf_pool_name) - 1;
    mbuf_pool_name[index_of_X] = char_i;
    unsigned nb_mbufs = 8192U;
    int ret = 0;
    mb_pool = rte_pktmbuf_pool_create(mbuf_pool_name, nb_mbufs,
                                              MEMPOOL_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE,
                                              rte_socket_id());
    if (mb_pool == NULL)
    {
        printf("fail to init mb_pool\n");
        rte_exit(EXIT_FAILURE, "%s\n", rte_strerror(rte_errno));
        return 0;
    }
    ret = rte_eth_rx_queue_setup(portid, 0, nb_rxd, rte_eth_dev_socket_id(portid), &rxq_conf, mb_pool);
    if (ret != 0)
    {
        printf("failed to init rx_queue\n");
    }

    index_of_X = strlen(tx_buffer_name) - 1;
    tx_buffer_name[index_of_X] = char_i;
    tx_buffer = rte_zmalloc_socket(tx_buffer_name,
                                           RTE_ETH_TX_BUFFER_SIZE(1), 0,
                                           rte_eth_dev_socket_id(portid));
    if (tx_buffer == NULL)
    {
        printf("fail to init buffer\n");
        return 0;
    }

}


// client is scaling on the number of ports
int dpdk_init_port_client(uint16_t portid)
{
    int ret = 0;
    int queueid = 0;
    struct rte_eth_dev_info dev_info;

    static struct rte_eth_conf local_port_conf = {
        .rxmode = {
            .split_hdr_size = 0,
        },
        .txmode = {
            .mq_mode = ETH_MQ_TX_NONE,
        },
    };
    ret = rte_eth_dev_info_get(portid, &dev_info);
    rxq_conf = dev_info.default_rxconf;
    rxq_conf.offloads = local_port_conf.rxmode.offloads;
    if (ret != 0)
        rte_exit(EXIT_FAILURE,
                 "Error during getting device (port %u) info: %s\n",
                 0, strerror(-ret));

    if (dev_info.tx_offload_capa & DEV_TX_OFFLOAD_MBUF_FAST_FREE)
        local_port_conf.txmode.offloads |=
            DEV_TX_OFFLOAD_MBUF_FAST_FREE;
    ret = rte_eth_dev_configure(portid, 1, 1, &local_port_conf);
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

    // init tx queue
    txq_conf = dev_info.default_txconf;
    txq_conf.offloads = local_port_conf.txmode.offloads;
    ret = rte_eth_tx_queue_setup(portid, queueid, nb_txd,
                                 rte_eth_dev_socket_id(portid),
                                 &txq_conf);
    if (ret != 0)
    {
        printf("failed to init queue\n");
        return 0;
    }
}

int are_macs_equal(struct rte_ether_addr* addr1, struct rte_ether_addr* addr2)
{
    return memcmp(&addr1->addr_bytes,&addr2->addr_bytes,sizeof(addr1->addr_bytes)) == 0;
}

//Process running on a single core that manages 1 NIC
static int
relay_job(__rte_unused void *arg)
{
    struct rte_mbuf *pkts_burst[32];
    int qid = 0;
    int portid = 0;
    int ret = 0;

    struct rte_ether_addr port_mac;
    
    if (rte_eth_macaddr_get(portid, &port_mac) != 0) {
        printf("Could not find MAC address for port %d\n", portid);
        return -1;
    }
    ret = rte_eth_tx_buffer_init(tx_buffer, 1);

    int pkts_recv;
    bool known_mac;

    while(true){
        pkts_recv = rte_eth_rx_burst(portid, qid, pkts_burst, MAX_PKT_BURST);
        for (int i = 0; i < pkts_recv; i++){
            known_mac = false;
            struct rte_ether_hdr *eth_hdr = rte_pktmbuf_mtod(pkts_burst[i], struct rte_ether_hdr *);
            for(int j = 0; j < 2; j++){
#if RTE_VERSION < RTE_VERSION_NUM(21, 11, 0, 0)
                
                if(are_macs_equal(&peer_addresses[j],&eth_hdr->s_addr)){
                    rte_ether_addr_copy(&peer_addresses[(j+1)%2], &eth_hdr->dst_addr);
                    rte_ether_addr_copy(&port_mac, &eth_hdr->s_addr);
                    known_mac = true;
                    
                }
#else 
                if(are_macs_equal(&peer_addresses[j],&eth_hdr->src_addr)){
                    rte_ether_addr_copy(&peer_addresses[(j+1)%2], &eth_hdr->dst_addr);
                    rte_ether_addr_copy(&port_mac, &eth_hdr->src_addr);
                    known_mac = true;
#endif
                }
            }
            if(known_mac){
                rte_eth_tx_buffer(portid, qid, tx_buffer, pkts_burst[i]);
            }
            else{
                printf("unknown mac : %x:%x:%x:%x:%x:%x\n",
                eth_hdr->src_addr.addr_bytes[0],
                eth_hdr->src_addr.addr_bytes[1],
                eth_hdr->src_addr.addr_bytes[2],
                eth_hdr->src_addr.addr_bytes[3],
                eth_hdr->src_addr.addr_bytes[4],
                eth_hdr->src_addr.addr_bytes[5]);
            }
            
        }
    }
}

int main(int argc, char **argv)
{
    unsigned portids[NB_OF_PORTS];
    unsigned index_lcore = 0;
    unsigned portid = 0;
    unsigned lcore_id;
    int ret = 0;
    ret = rte_eal_init(argc, argv);
        if (ret < 0)
            rte_panic("Cannot init EAL\n");
        argc -= ret;
        argv += ret;
        printf("EAL setup finshed\n");
    if(argc != 3){
        printf("Wrong number of arguments : expected : 3, given : %d\n",argc);
        return -1;
    }
     
    str_to_mac(argv[1], &peer_addresses[0]);
    str_to_mac(argv[2], &peer_addresses[1]);
    
    
    dpdk_init_port_client(portid);
    dpdk_init_mbuf_txbuffer(portid);
    ret = rte_eth_dev_start(portid);
    if (ret != 0)
    {
        printf("failed to start device\n");
    }
    RTE_LCORE_FOREACH_WORKER(lcore_id)
    {
        rte_eal_remote_launch(relay_job, NULL, lcore_id);
    }

    rte_eal_mp_wait_lcore();

    /* clean up the EAL */
    rte_eal_cleanup();

    return 0;
}
