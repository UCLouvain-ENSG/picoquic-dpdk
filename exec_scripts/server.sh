#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH perf record -o perfMeasures/perfServerTPNoDPDK.data -g ./dpdk_picoquicdemo --nodpdk -p 4443 -1
