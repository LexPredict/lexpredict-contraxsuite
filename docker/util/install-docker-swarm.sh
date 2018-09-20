#!/bin/bash

echo "Setting up Docker Swarm cluster."
echo "Here are the ip addresses this machine has:"
sudo ip addr show
echo "Enter internal ip of this host by which other cluster hosts can access it (leave blank if only one ip addr on the main network interface): "
read DOCKER_SWARM_ADVERTISE_ADDR

sudo docker swarm init --advertise-addr=${DOCKER_SWARM_ADVERTISE_ADDR}
