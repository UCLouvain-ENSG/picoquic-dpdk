#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH perf record -o perfMeasures/perfClientTPNoDPDK.data -g ./dpdk_picoquicdemo --nodpdk -D -A 50:6b:4b:f3:7c:71 10.100.0.2 4443 /20000000000
