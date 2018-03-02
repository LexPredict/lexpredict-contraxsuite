#!/bin/bash

#set -e

echo "=== This script will setup a new Contraxsuite instance"
echo ""
source setenv.sh

echo "=== Installing Docker..." -r
source ./util/install-docker-ubuntu.sh
echo ""

echo "=== Creating user shared between Docker containers and host machine..."
source ./util/install-docker-shared-user.sh

echo "=== Initializing Docker Swarm cluster..."
source ./util/install-docker-swarm.sh

echo "=== Pulling contraxsuite image from DockerHub "
sudo docker pull ${CONTRAXSUITE_IMAGE}


echo "=== Deploying Contraxsuite stack to Docker Swarm..."
pushd ./deploy
    source deploy-contraxsuite-to-swarm-cluster.sh
popd
