sudo echo 3 | sudo tee /sys/bus/pci/devices/0000:18:00.0/sriov_numvfs ;\
sudo ip netns add nsCLIENT ;\
sudo ip netns add nsSERVER ;\
sudo ip link set ens1f0v0 netns nsCLIENT ;\
sudo ip link set ens1f0v1 netns nsSERVER ;\
sudo ip link set ens1f0v2 netns nsSERVER ;\
sudo ip netns exec nsCLIENT sudo ifconfig ens1f0v0 10.10.0.1 netmask 255.255.255.0 ;\
sudo ip netns exec nsSERVER sudo ifconfig ens1f0v1 10.10.0.3 netmask 255.255.255.0 ;\
sudo ip netns exec nsCLIENT sudo arp -s 10.10.0.4 12:a6:8f:dd:ec:1a