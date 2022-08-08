#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 5-7 -a 0000:18:00.3 -a 0000:18:00.4 --proc-type=primary --file-prefix=rte_2 --socket-mem=2000 -- -2 2e:78:89:81:61:eb -a proxy -p 4443 
