#!/bin/bash

#set -e

echo "=== This script will update local Contraxsuite instance to the latest public docker image"

echo "=== Assume Contraxsuite is configured in ./setenv_local.sh file."

source ./setenv.sh

if [ ! -z "${DISTR_DOCKER_IMAGE_URL}" ]; then
    echo "=== Downloading Contraxsuite image from dist server"
    wget -qO- --user=${DISTR_USER} --password=${DISTR_PASSWORD} ${DISTR_DOCKER_IMAGE_URL} | sudo docker load

    if [ "${DISTR_DOCKER_IMAGE_NAME}" != "${CONTRAXSUITE_IMAGE_FULL_NAME}" ]; then
        echo "Tagging contraxsuite image as: ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest"
        sudo docker tag ${DISTR_DOCKER_IMAGE_NAME}:latest ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest
    fi

    if [ ! -z "${DOCKER_REGISTRY}" ]; then
        echo "Pushing ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest to its registry..."
        sudo docker push ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest
    fi
else
    echo "=== Pulling contraxsuite image from DockerHub "
    sudo docker pull ${CONTRAXSUITE_IMAGE_FULL_NAME}
fi


echo "=== Deploying Contraxsuite stack to Docker Swarm..."
pushd ./deploy
    source deploy-contraxsuite-to-swarm-cluster.sh
popd
