#!/bin/bash

#set -e

echo "=== This script will update local Contraxsuite instance to the latest docker image"

echo "=== Assume Contraxsuite is configured in ./setenv_local.sh file."

source ./setenv.sh

echo "=== Pulling contraxsuite image from DockerHub "
sudo docker pull ${CONTRAXSUITE_IMAGE}


echo "=== Deploying Contraxsuite stack to Docker Swarm..."
pushd ./deploy
    source deploy-contraxsuite-to-swarm-cluster.sh
popd
