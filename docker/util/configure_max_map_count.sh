#!/bin/bash

echo "vm.max_map_count=262144" | sudo tee --append /etc/sysctl.conf
sudo sysctl -w vm.max_map_count=262144