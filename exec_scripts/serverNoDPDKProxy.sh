#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 0-2 -a 0000:18:00.4 -- -! -2 2e:78:89:81:61:eb -a proxy -p 4443 
