#!/bin/bash
sudo valgrind ./dpdk_picoquicdemo -l 0-4 -a 0000:51:00.0 -- -p 4443