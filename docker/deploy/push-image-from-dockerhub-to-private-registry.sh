#!/bin/bash

set -e
source ../setenv.sh
if [ -e ../setenv_local.sh ]
then
    source ../setenv_local.sh
fi

read -p "Enter Dockerhub username/repository: " -r
DOCKER_HUB_REPO=${REPLY}

if [ -z ${DOCKER_HUB_REPO} ]; then
    REMOTE_IMAGE=${CONTRAXSUITE_IMAGE}
else
    REMOTE_IMAGE=${DOCKER_HUB_REPO}/${CONTRAXSUITE_IMAGE}
fi

echo "Please login to DockerHub..."
sudo docker login

echo "Pulling from DockerHub..."
sudo docker pull ${REMOTE_IMAGE}:latest

echo "Tagging image..."
sudo docker tag ${REMOTE_IMAGE}:latest ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest

echo "Pushing to ${DOCKER_REGISTRY}..."
sudo docker push ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest
