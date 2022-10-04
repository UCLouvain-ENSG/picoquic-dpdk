#!/bin/bash
sudo taskset -c 2 sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --nodpdk -p 4443
