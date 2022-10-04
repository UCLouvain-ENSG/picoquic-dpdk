#!/bin/bash
sudo perf record --call-graph dwarf -o perfMeasures/nodpdk_client_no_GSO.data sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --nodpdk -0 -D -A 50:6b:4b:f3:7c:71 10.100.0.2 4443 /20000000000
