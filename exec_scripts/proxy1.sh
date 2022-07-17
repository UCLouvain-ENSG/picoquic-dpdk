#32:af:e5:33:4f:ac => directlink
#8a:37:d5:09:9b:31 => proxylink
sudo LD_LIBRARY_PATH=$LD_LIBRARY_PATH ./udpsender -l 0-1 -a 0000:51:00.4 --proc-type=primary --file-prefix=rte_0 --socket-mem=2000 -- 8a:37:d5:09:9b:31 1000 7000 100

