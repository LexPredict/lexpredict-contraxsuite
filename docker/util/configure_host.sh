#!/bin/bash


sudo grep -q -F 'vm.max_map_count=262144' /etc/sysctl.conf || echo 'vm.max_map_count=262144' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.max_map_count=262144

sudo grep -q -F 'vm.overcommit_memory=1' /etc/sysctl.conf || echo 'vm.overcommit_memory=1' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.overcommit_memory=1

sudo grep -q -F 'vm.swappiness=0' /etc/sysctl.conf || echo 'vm.swappiness=0' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.swappiness=0


sudo grep -q -F 'net.ipv4.tcp_keepalive_time=600' /etc/sysctl.conf || echo 'net.ipv4.tcp_keepalive_time=600' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w net.ipv4.tcp_keepalive_time=600

sudo grep -q -F 'net.ipv4.tcp_keepalive_intvl=60' /etc/sysctl.conf || echo 'net.ipv4.tcp_keepalive_intvl=60' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w net.ipv4.tcp_keepalive_intvl=60

sudo grep -q -F 'net.ipv4.tcp_keepalive_probes=3' /etc/sysctl.conf || echo 'net.ipv4.tcp_keepalive_probes=3' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w net.ipv4.tcp_keepalive_probes=3

sudo grep -q -F 'net.ipv6.conf.all.disable_ipv6=1' /etc/sysctl.conf || echo 'net.ipv6.conf.all.disable_ipv6=1' | sudo tee --append /etc/sysctl.conf
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1



echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

echo "#!/bin/sh" | sudo tee /etc/rc.local
echo "echo never > /sys/kernel/mm/transparent_hugepage/enabled" | sudo tee --append /etc/rc.local