sudo echo 3 | sudo tee /sys/bus/pci/devices/0000:18:00.0/sriov_numvfs
sudo ip netns add nsSERVER
sudo ip link set ens1f0v2 netns nsSERVER
sudo ip netns exec nsSERVER ifconfig ens1f0v2 3.0.0.1 netmask 255.255.255.0
sudo ip netns exec nsSERVER sudo ip route add 1.0.0.0/24 dev ens1f0v2
sudo ip netns exec nsSERVER arp -s 1.0.0.1 7e:62:74:e3:f6:91

sudo ifconfig ens1f0v0 up
sudo ifconfig ens1f0v1 2.0.0.1 netmask 255.255.255.0
