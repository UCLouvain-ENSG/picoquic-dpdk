#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 5-7 -a 0000:8a:02.4 -a 0000:8a:02.5 --proc-type=primary --file-prefix=rte_2 --socket-mem=2000 -- -2 32:af:e5:33:4f:ac -! -a proxy -p 4443 
