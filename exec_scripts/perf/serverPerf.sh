#!/bin/bash
sudo perf record --call-graph dwarf -o perfMeasures/nodpdk_server_no_GSO.data sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --nodpdk -0 -p 4443 -1
