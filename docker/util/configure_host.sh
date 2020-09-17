#!/bin/bash

# Configure various host parameters required for normal Docker and Contraxsuite functioning

# This script is assumed to be run with sudo.
# This script is used for embedding into the worker init script.
# Please keep it simple and don't source other scripts from this one.

grep -q -F 'vm.max_map_count=262144' /etc/sysctl.conf || echo 'vm.max_map_count=262144' | tee --append /etc/sysctl.conf
sysctl -w vm.max_map_count=262144

grep -q -F 'vm.overcommit_memory=1' /etc/sysctl.conf || echo 'vm.overcommit_memory=1' | tee --append /etc/sysctl.conf
sysctl -w vm.overcommit_memory=1

grep -q -F 'vm.swappiness=0' /etc/sysctl.conf || echo 'vm.swappiness=0' | tee --append /etc/sysctl.conf
sysctl -w vm.swappiness=0


grep -q -F 'net.ipv4.tcp_keepalive_time=600' /etc/sysctl.conf || echo 'net.ipv4.tcp_keepalive_time=600' | tee --append /etc/sysctl.conf
sysctl -w net.ipv4.tcp_keepalive_time=600

grep -q -F 'net.ipv4.tcp_keepalive_intvl=60' /etc/sysctl.conf || echo 'net.ipv4.tcp_keepalive_intvl=60' | tee --append /etc/sysctl.conf
sysctl -w net.ipv4.tcp_keepalive_intvl=60

grep -q -F 'net.ipv4.tcp_keepalive_probes=3' /etc/sysctl.conf || echo 'net.ipv4.tcp_keepalive_probes=3' | tee --append /etc/sysctl.conf
sysctl -w net.ipv4.tcp_keepalive_probes=3

grep -q -F 'net.ipv6.conf.all.disable_ipv6=1' /etc/sysctl.conf || echo 'net.ipv6.conf.all.disable_ipv6=1' | tee --append /etc/sysctl.conf
sysctl -w net.ipv6.conf.all.disable_ipv6=1



echo never | tee /sys/kernel/mm/transparent_hugepage/enabled

echo "#!/bin/sh" | tee /etc/rc.local
echo "echo never > /sys/kernel/mm/transparent_hugepage/enabled" | tee --append /etc/rc.local