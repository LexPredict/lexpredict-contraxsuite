#!/bin/bash

#set -e

echo "=== This script will prepare a new Contraxsuite cluster based on Docker Swarm"
echo "=== It is intended to be run on an empty Ubuntu 16.04 - 16.10 machine."

echo "=== Please configure Contraxsute in ../setenv_local.sh file."
read -p "=== Config file will be opened in \"nano\" editor. Press enter to continue..." -r
if [ ! -e ../setenv_local.sh ]; then
    sed -e 's/^/#/' ../setenv.sh > ../setenv_local.sh
fi
nano ../setenv_local.sh
echo ""
echo "=== Installing Docker..." -r
source ../util/install-docker-ubuntu.sh
echo ""

echo "=== Creating user shared between Docker containers and host machine..."
source ../util/install-docker-shared-user.sh

echo "=== Initializing Docker Swarm cluster..."
source ../util/install-docker-swarm.sh

echo "=== Installing Docker private registry..."
echo "This private registry works over plain HTTP. Please take care about security in the local network."
source ../util/allow-insecure-registry.sh
source ../util/install-docker-registry.sh

echo "=== Deploying Swarmpit (Docker Swarm Management Web App)..."
source ../util/install-swarmpit.sh

echo "=== Putting contraxsuite app image from DockerHub to private registry..."
source push-image-from-dockerhub-to-private-registry.sh

echo "=== Deploying Contraxsuite stack to Docker Swarm..."
source deploy-contraxsuite-to-swarm-cluster.sh

echo "==="
echo "Please execute the following steps to add a worker node to this cluster:"
echo "1. Ensure the worker node has network access to private Docker registry ${DOCKER_REGISTRY}"
echo "2. Install Docker to worker node machine (install-docker-ubuntu.sh)."
echo "3. Make required config: allow-insecure-registry.sh, configure_host.sh"
echo "4. Connect node to this cluster:"
sudo docker swarm join-token worker
echo "(please replace IP address with the host name of this machine to avoid problems with dynamic IPs - probably $(hostname))"
echo "==="

