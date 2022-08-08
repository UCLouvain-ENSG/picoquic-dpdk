sudo echo 3 | sudo tee /sys/bus/pci/devices/0000:18:00.0/sriov_numvfs ;\

sudo ifconfig ens1f0v1 2.0.0.1 netmask 255.255.255.0 ;\
sudo ifconfig ens1f0v2 3.0.0.1 netmask 255.255.255.0 ;\
