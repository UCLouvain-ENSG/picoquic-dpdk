#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 0-2 -a 0000:18:00.2 -- -! -A 46:6b:95:10:ba:95 -2 fe:13:bc:b6:46:cd -a proxy 2.0.0.2 4443 /10000000000
