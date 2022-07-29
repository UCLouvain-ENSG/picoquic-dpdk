#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 5-7 -a 0000:18:02.4 -a 0000:18:02.5 --proc-type=primary --file-prefix=rte_2 --socket-mem=2000 -- -2 46:6b:95:10:ba:95 -a proxy -p 4443 
