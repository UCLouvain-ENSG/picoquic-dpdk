#!/bin/bash
sudo perf record --call-graph dwarf -o perfMeasures/dpdk_client.data sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 0-1 -a 0000:18:00.0 -- -X -D -A 50:6b:4b:f3:7c:70 -* 32 -@ 32 10.100.0.2 4443 /60000000000
#sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 0-8 -a 0000:18:00.2 -a 0000:18:00.3 -a 0000:18:00.4 -a 0000:18:00.5 -a 0000:18:00.6 -a 0000:18:00.7 -a 0000:18:01.0 -a 0000:18:01.1 -- -D -A 50:6b:4b:f3:7c:70 -* 32 -@ 4 10.100.0.2 4443 /200
