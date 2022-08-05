sudo echo 2 | sudo tee /sys/bus/pci/devices/0000:18:00.0/sriov_numvfs
sudo ip netns add nsCLIENT
sudo ip netns add nsSERVER
sudo ip link set ens1f0v0 netns nsCLIENT
sudo ip link set ens1f0v1 netns nsSERVER
sudo ip netns exec nsCLIENT sudo ifconfig ens1f0v0 1.0.0.1 netmask 255.255.255.0
sudo ip netns exec nsSERVER sudo ifconfig ens1f0v1 2.0.0.1 netmask 255.255.255.0

sudo ip netns exec nsCLIENT sudo ip route add 2.0.0.0/24 dev ens1f0v0
sudo ip netns exec nsSERVER sudo ip route add 1.0.0.0/24 dev ens1f0v1

sudo ip netns exec nsCLIENT sudo arp -s 2.0.0.1 12:a6:8f:dd:ec:1a 
sudo ip netns exec nsSERVER sudo arp -s 1.0.0.1 de:da:d4:29:5a:f2

sudo ip netns exec nsCLIENT sudo ip route add 7.0.0.0/24 dev ens1f0v0
sudo ip netns exec nsSERVER sudo ip route add 7.0.0.0/24 dev ens1f0v1

sudo ip netns exec nsCLIENT sudo arp -s 7.0.0.1 12:a6:8f:dd:ec:1a
sudo ip netns exec nsSERVER sudo arp -s 7.0.0.2 de:da:d4:29:5a:f2