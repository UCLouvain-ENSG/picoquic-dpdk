sudo echo 3 | sudo tee /sys/bus/pci/devices/0000:18:00.0/sriov_numvfs
sudo ip netns add nsCLIENT
sudo ip link set ens1f0v0 netns nsCLIENT
sudo ip netns exec nsCLIENT ifconfig ens1f0v0 1.0.0.1 netmask 255.255.255.0
sudo ip netns exec nsCLIENT sudo ip route add 3.0.0.0/24 dev ens1f0v0
sudo ip netns exec nsCLIENT arp -s 3.0.0.1 12:a6:8f:dd:ec:1a

sudo ifconfig ens1f0v1 2.0.0.2 netmask 255.255.255.0
sudo ifconfig ens1f0v2 up