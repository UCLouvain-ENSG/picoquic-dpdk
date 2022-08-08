
#!/bin/bash
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./dpdk_picoquicdemo --dpdk -l 2-4 -a 0000:18:00.2 -a 0000:18:00.3 --proc-type=primary --file-prefix=rte_1 --socket-mem=2000 -- -A 2e:78:89:81:61:eb -2 fe:13:bc:b6:46:cd -a proxy 10.100.0.2 4443 /10000000000
#sudo ./dpdk_picoquicdemo dpdk -l 0-8 -a 0000:51:00.2 -a 0000:51:00.3 -a 0000:51:00.4 -a 0000:51:00.5 -a 0000:51:00.6 -a 0000:51:00.7 -a 0000:51:01.0 -a 0000:51:01.1  -- -A 50:6b:4b:f3:7c:70 -D localhost 4443 /1000000000
