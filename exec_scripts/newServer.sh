#!/bin/bash
sudo ./dpdk_picoquicdemo dpdk -l 0-1 -a 0000:51:00.1 -- -q qlogs -p 4443 
