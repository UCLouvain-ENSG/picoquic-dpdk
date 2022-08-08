sudo echo 3 | sudo tee /sys/bus/pci/devices/0000:18:00.0/sriov_numvfs
sudo ip netns add nsCLIENT ;\
sudo ip netns add nsSERVER ;\
sudo ip link set ens1f0v0 netns nsCLIENT ;\
sudo ip link set ens1f0v1 netns nsSERVER ;\

sudo ip netns exec nsCLIENT wg-quick up wg2
sudo ip netns exec nsCLIENT ifconfig ens1f0v0 2.0.0.1 netmask 255.255.255.0
sudo ip netns exec nsSERVER ifconfig ens1f0v1 3.0.0.1 netmask 255.255.255.0

sudo ip netns exec nsCLIENT sudo ip route add 1.0.0.0/24 dev ens1f0v0
sudo ip netns exec nsSERVER sudo ip route add 1.0.0.0/24 dev ens1f0v1
sudo ip netns exec nsCLIENT sudo ip route add 3.0.0.0/24 via 6.0.0.2


sudo ip netns exec nsCLIENT arp -s 1.0.0.1 fe:13:bc:b6:46:cd
sudo ip netns exec nsSERVER arp -s 1.0.0.1 46:6b:95:10:ba:95