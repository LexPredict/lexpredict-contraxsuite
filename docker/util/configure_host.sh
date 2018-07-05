#!/bin/bash


sudo grep -q -F 'vm.max_map_count=262144' /etc/sysctl.conf || echo 'vm.max_map_count=262144' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.max_map_count=262144

sudo grep -q -F 'vm.overcommit_memory=1' /etc/sysctl.conf || echo 'vm.overcommit_memory=1' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.overcommit_memory=1

sudo grep -q -F 'vm.swappiness=0' /etc/sysctl.conf || echo 'vm.swappiness=0' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.swappiness=0


echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

echo "#!/bin/sh" | sudo tee /etc/rc.local
echo "echo never > /sys/kernel/mm/transparent_hugepage/enabled" | sudo tee --append /etc/rc.local