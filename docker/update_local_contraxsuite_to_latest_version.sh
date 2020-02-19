#!/bin/bash

#set -e

echo "=== This script will update local Contraxsuite instance to the latest public docker image"

echo "=== Assume Contraxsuite is configured in ./setenv_local.sh file."

source ./setenv.sh

if [ ! -z "${DISTR_DOCKER_IMAGE_URL}" ]; then
    # Let the script exit immediately if any error occurs with pushing the image to the local repo.
    # Otherwise we can have the cluster partially working and experience errors on worker machine connections.
    set -e
    echo "=== Downloading Contraxsuite image from dist server"
    rm -f ./image.tar
    wget --user=${DISTR_USER} --password=${DISTR_PASSWORD} ${DISTR_DOCKER_IMAGE_URL} -O ./image.tar
    sudo docker load < image.tar
    rm -f ./image.tar

    if [ "${DISTR_DOCKER_IMAGE_NAME}" != "${CONTRAXSUITE_IMAGE_FULL_NAME}" ]; then
        echo "Tagging contraxsuite image as: ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION}"
        sudo docker tag ${DISTR_DOCKER_IMAGE_NAME}:latest ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION}
    fi

    if [ ! -z "${DOCKER_REGISTRY}" ]; then
        echo "Pushing ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION} to its registry..."
        sudo docker push ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION}
    fi
    set +e
else
    echo "=== Pulling contraxsuite image from DockerHub "
    sudo docker pull ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION}
fi


echo "=== Deploying Contraxsuite stack to Docker Swarm..."
pushd ./deploy
    source deploy-contraxsuite-to-swarm-cluster.sh
popd
