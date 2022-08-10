/*
* Author: Christian Huitema
* Copyright (c) 2019, Private Octopus, Inc.
* All rights reserved.
*
* Permission to use, copy, modify, and distribute this software for any
* purpose with or without fee is hereby granted, provided that the above
* copyright notice and this permission notice appear in all copies.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
* ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL Private Octopus, Inc. BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
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
#include <rte_udp.h>
#include <rte_ip.h>
#include <rte_errno.h>

#include <rte_common.h>
#include <rte_byteorder.h>
#include <rte_log.h>
#include <rte_memory.h>
#include <rte_memcpy.h>
#include <rte_memzone.h>
#include <rte_eal.h>
#include <rte_per_lcore.h>
#include <rte_launch.h>
#include <rte_atomic.h>
#include <rte_cycles.h>
#include <rte_prefetch.h>
#include <rte_lcore.h>
#include <rte_per_lcore.h>
#include <rte_branch_prediction.h>
#include <rte_interrupts.h>
#include <rte_pci.h>
#include <rte_random.h>
#include <rte_debug.h>
#include <rte_ether.h>
#include <rte_ethdev.h>
#include <rte_ring.h>
#include <rte_mempool.h>
#include <rte_mbuf.h>
#include <rte_ip.h>
#include <rte_tcp.h>
#include <rte_udp.h>
#include <rte_string_fns.h>
#include <rte_timer.h>
#include <rte_power.h>
#include <rte_eal.h>
#include <rte_spinlock.h>
#include <rte_version.h>

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include "picoquic_internal.h"
#include "proxy.h"


uint32_t tx_ip_src_addr_tmp = (198U << 24) | (18 << 16) | (0 << 8) | 1;
uint32_t tx_ip_dst_addr_tmp = (198U << 24) | (18 << 16) | (0 << 8) | 2;

uint16_t tx_udp_src_port_tmp = 9;
uint16_t tx_udp_dst_port_tmp = 9;

#define IP_DEFTTL_tmp 64

// int rcv_encapsulate_send(picoquic_cnx_t* cnx,proxy_ctx_t * ctx, uint8_t* bytes, size_t available) {
//     int length = 0;
//     int udp_dgram_offset = sizeof(struct rte_ipv4_hdr) + sizeof(struct rte_udp_hdr);
//     int MAX_PKT_BURST = 32;
//     struct rte_mbuf *pkts_burst[MAX_PKT_BURST];
//     struct rte_ether_addr eth_addr;
//     // printf("portid : %d\n",ctx->portid);
//     int ret = rte_eth_macaddr_get(ctx->portid, &eth_addr);


//     // char macStr[18];

//     // snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x", eth_addr.addr_bytes[0], 
//     //                                                                 eth_addr.addr_bytes[1], 
//     //                                                                 eth_addr.addr_bytes[2], 
//     //                                                                 eth_addr.addr_bytes[3], 
//     //                                                                 eth_addr.addr_bytes[4], 
//     //                                                                 eth_addr.addr_bytes[5]);

//     printf("here??\n")                                                                 
//     int nb_rx = (int)rte_ring_dequeue_burst(ctx->rx_to_worker_ring, (void**)pkts_burst, MAX_PKT_BURST, NULL);
//     // printf("trying to receive\n");
    
//     // printf("mac : %s\n",macStr);
//     // int recv_counter = 0;
//     // while(recv)
//     //     recv_counter
//     // }
//     ;
//     for (int j = 0; j < nb_rx; j++)
//     {
//         printf("received ring\n");
//         struct rte_ether_hdr *eth_hdr = rte_pktmbuf_mtod(pkts_burst[j], struct rte_ether_hdr *);
//         if (eth_hdr->ether_type == rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4)){
//             int ret = 0;
//             struct rte_ipv4_hdr *ip_hdr;
//             ip_hdr = (struct rte_ipv4_hdr *)(rte_pktmbuf_mtod(pkts_burst[j], char *) + sizeof(struct rte_ether_hdr));

//             struct rte_udp_hdr *udp = (struct rte_udp_hdr *)((unsigned char *)ip_hdr +
//                                                             sizeof(struct rte_ipv4_hdr));
//             unsigned char *payload = (unsigned char *)(udp + 1);

//             int msg;
// 			memcpy(&msg,payload,4);
			

//             length = htons(ip_hdr->total_length);
//             //printf("length : %d\n",pkts_burst[j]->pkt_len);
//             ret = picoquic_queue_datagram_frame(cnx, length, ip_hdr);
//             ctx->counter++;
//             // if(ctx->counter % 10000 == 0){
//             //     printf("packet : %lu\n",ctx->counter);
//             // }
            
//             rte_pktmbuf_free(pkts_burst[j]);
//             if(length > 1300){
//                 printf("error\n");
//             }
//             //printf("payload : %s\n",payload);
            
//         }
//     }
//     return 0; 
// }

int rcv_encapsulate_send2(picoquic_cnx_t* cnx,proxy_ctx_t * ctx, uint8_t* bytes, size_t available) {
    int length = 0;
    int udp_dgram_offset = sizeof(struct rte_ipv4_hdr) + sizeof(struct rte_udp_hdr);
    int MAX_PKT_BURST = 32;
    struct rte_mbuf *pkt[1];
    struct rte_ether_addr eth_addr;
    // printf("portid : %d\n",ctx->portid);
    int ret = rte_eth_macaddr_get(ctx->portid, &eth_addr);


    // char macStr[18];

    // snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x", eth_addr.addr_bytes[0], 
    //                                                                 eth_addr.addr_bytes[1], 
    //                                                                 eth_addr.addr_bytes[2], 
    //                                                                 eth_addr.addr_bytes[3], 
    //                                                                 eth_addr.addr_bytes[4], 
    //                                                                 eth_addr.addr_bytes[5]);

                      

    uint32_t n = rte_ring_dequeue_bulk_start(ctx->rx_to_worker_ring, &pkt, 1, NULL);
    if (n != 0) {
        struct rte_ether_hdr *eth_hdr = rte_pktmbuf_mtod(pkt[0], struct rte_ether_hdr *);
        if (eth_hdr->ether_type == rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4)){
            int ret = 0;
            struct rte_ipv4_hdr *ip_hdr;
            ip_hdr = (struct rte_ipv4_hdr *)(rte_pktmbuf_mtod(pkt[0], char *) + sizeof(struct rte_ether_hdr));

            struct rte_udp_hdr *udp = (struct rte_udp_hdr *)((unsigned char *)ip_hdr +
                                                            sizeof(struct rte_ipv4_hdr));
            unsigned char *payload = (unsigned char *)(udp + 1);

            length = htons(ip_hdr->total_length);
            if(length > 1300){
                printf("error\n");
                return -1;
            }
            
            //printf("length : %d\n",pkts_burst[j]->pkt_len);
            if(length<available){
                bytes = picoquic_provide_datagram_buffer(bytes, length);

                if(bytes != NULL){
                    rte_memcpy(bytes,ip_hdr,length);
                    rte_ring_dequeue_finish(ctx->rx_to_worker_ring, n);
                    uint32_t msg;
                    memcpy(&msg,payload,4);
                    // if(msg != ctx->counter){
                    //         printf("loss detected at packet %u\n",ctx->counter);
                    //         printf("expected : %u\n",ctx->counter);
                    //         printf("actual : %u\n",msg);
                    //         printf("packet lost\n");
                    //         exit(0);
                    // }
                    ctx->counter++;
                    
                }
                else{
                    rte_ring_dequeue_finish(ctx->rx_to_worker_ring, n);
                    printf("MALLOC FAILED\n");
                }
                rte_pktmbuf_free(pkt[0]);
            }
            else{
                rte_ring_dequeue_finish(ctx->rx_to_worker_ring, 0);
            }
            
        }
        else{
            rte_ring_dequeue_finish(ctx->rx_to_worker_ring, n);
            rte_pktmbuf_free(pkt[0]);

        }      
    }
    return 0; 
}

void copy_buf_to_pkt_simple(void *buf, unsigned len, struct rte_mbuf *pkt, unsigned offset)
{

    rte_memcpy(rte_pktmbuf_mtod_offset(pkt, char *, offset),
               buf, (size_t)len);
    return;
}
int send_received_dgram(proxy_ctx_t *ctx, uint8_t *ip_packet) {

    struct rte_mbuf *m;
    struct rte_ether_hdr *eth_hdr;
    struct rte_ipv4_hdr *ip_hdr;
    struct rte_udp_hdr *udp_hdr;
    struct rte_ether_addr eth_addr;
    int length = 0;
    int udp_dgram_offset = sizeof(struct rte_ipv4_hdr);
    int ret = rte_eth_macaddr_get(ctx->portid, &eth_addr);
    m = rte_pktmbuf_alloc(ctx->mb_pool);
    if (m == NULL)
    {
        printf("fail to init pktmbuf\n");
        rte_exit(EXIT_FAILURE, "%s\n", rte_strerror(rte_errno));
        return 0;
    }
    
    eth_hdr = (struct rte_ether_hdr *)(rte_pktmbuf_mtod(m, char *));
    //memset(eth_hdr,0,sizeof(struct rte_ether_hdr));
    eth_hdr -> ether_type = rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4);
#if RTE_VERSION < RTE_VERSION_NUM(21,11,0,0)
    rte_ether_addr_copy(&eth_addr, &eth_hdr->s_addr);
    rte_ether_addr_copy(ctx->client_addr, &eth_hdr->d_addr);
#else
    rte_ether_addr_copy(&eth_addr, &eth_hdr->src_addr);
    rte_ether_addr_copy(ctx->client_addr, &eth_hdr->dst_addr);
#endif

    // char macStr[18];
    // char macStrSrc[18];
    // snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x", (&eth_hdr->src_addr)->addr_bytes[0], 
    //                                                                 (&eth_hdr->src_addr)->addr_bytes[1], 
    //                                                                 (&eth_hdr->src_addr)->addr_bytes[2], 
    //                                                                 (&eth_hdr->src_addr)->addr_bytes[3], 
    //                                                                 (&eth_hdr->src_addr)->addr_bytes[4], 
    //                                                                 (&eth_hdr->src_addr)->addr_bytes[5]);

    ip_hdr = (struct rte_ipv4_hdr *) ip_packet;
    length = htons(ip_hdr->total_length);
    //printf("length : %d\n",length);
    struct rte_udp_hdr *udp = (struct rte_udp_hdr *)((unsigned char *)ip_hdr +
															 sizeof(struct rte_ipv4_hdr));
	//unsigned char *payload = (unsigned char *)(udp + 1);
    //printf("payload : %s\n",payload);
    int payload_length = htons(udp->dgram_len) - sizeof(struct rte_udp_hdr);
    //setup_pkt_udp_ip_headers_tmp(ip_hdr,udp,payload_length);
    // printf("l1 : %d\n",length);
    // printf("l2 : %d\n", payload_length + sizeof(struct rte_ipv4_hdr));

    copy_buf_to_pkt_simple(ip_packet, length, m, sizeof(struct rte_ether_hdr));
    
    m->data_len = length+sizeof(struct rte_ether_hdr);
    m->pkt_len = length+sizeof(struct rte_ether_hdr);
    //printf("length : %d\n",m->pkt_len);
    // ctx->counter++;
    // if(ctx->counter % 10000 == 0){
    //     printf("counter : %ld\n",ctx->counter);
    // }
    
    ret = rte_eth_tx_burst(ctx->portid, ctx->queueid, &m,1);
    if(ret != 1){
        printf("=big ERROR==========\n");
    }
}


// proxy_ctx_t* proxy_create_ctx(proxy_struct_t *proxy_struct)
// {
//     proxy_ctx_t* ctx = (proxy_ctx_t*)malloc(sizeof(proxy_ctx_t));

//     if (ctx != NULL) {* Process the datagram, which contains an address and a QUIC packet */
//         memset(ctx, 0, sizeof(proxy_ctx_t));
//         ctx->portid = proxy_struct->portid;
//         ctx-> queueid = proxy_struct->queueid;
//         ctx-> mb_pool = proxy_struct->mb_pool;
//         ctx-> client_addr = proxy_struct->eth_client_proxy_addr;
//     }
//     return ctx;
// }

/*
 * proxy call back.
 */
int proxy_callback(picoquic_cnx_t* cnx,
    uint64_t stream_id, uint8_t* bytes, size_t length,
    picoquic_call_back_event_t fin_or_event, void* callback_ctx, void* v_stream_ctx)
{
    //printf("length : %d\n",length);
    int ret = 0;
    proxy_ctx_t * ctx = (proxy_ctx_t*)callback_ctx;
    if (ret == 0) {
        switch (fin_or_event) {
        case picoquic_callback_stream_data:
        case picoquic_callback_stream_fin:
        case picoquic_callback_stream_reset: /* Client reset stream #x */
        case picoquic_callback_stop_sending: /* Client asks server to reset stream #x */
        case picoquic_callback_stream_gap:
        case picoquic_callback_prepare_to_send:
           printf("Unexpected callback, code %d, length = %zu", fin_or_event, length);
           break;
        case picoquic_callback_prepare_datagram:
            //printf("callb\n");

            rcv_encapsulate_send2(cnx,ctx,bytes,length);
            break;
        case picoquic_callback_stateless_reset:
        case picoquic_callback_close: /* Received connection close */
        case picoquic_callback_application_close: /* Received application close */
            printf("app closed\n");
            // if (ctx != NULL) {
            //     free(ctx);
            //     ctx = NULL;
            // }
            picoquic_set_callback(cnx, NULL, NULL);
            break;
        case picoquic_callback_version_negotiation:
            break;
        case picoquic_callback_almost_ready:
            break;
        case picoquic_callback_ready:
            ctx->counter = 0;
            picoquic_mark_datagram_ready(cnx,1);
            break;
        case picoquic_callback_datagram:
            if(!cnx->client_mode){
                //printf("length : %lu\n",length);
            }
            send_received_dgram(ctx,bytes);
            break;
        case picoquic_callback_datagram_acked:
            // printf("acked datagram\n");
            break;
        default:
            // printf("even : %d\n",fin_or_event);
            // printf("inside default\n");
            /* unexpected */
            break;
        }
    }

    return ret;
}