#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 0-1 -a 0000:18:00.0 --  -* 32 -@ 32 -p 4443 -1
