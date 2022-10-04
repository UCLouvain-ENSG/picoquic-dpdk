#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --nodpdk -B 1000000000 -D -A 50:6b:4b:f3:7c:71 10.100.0.2 4443 /20000000000
