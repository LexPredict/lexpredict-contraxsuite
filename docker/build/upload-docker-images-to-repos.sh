#!/bin/bash

source ../setenv.sh
if [ -e ../setenv_local.sh ]
then
    source ../setenv_local.sh
fi

sudo docker login --username=${DOCKER_USERNAME} ${DOCKER_REGISTRY}

echo ""
echo "Local images with name: ${CONTRAXSUITE_IMAGE}: "
sudo docker images ${CONTRAXSUITE_IMAGE}
echo ""


CONTRAXSUITE_APP_ID=$(sudo docker images -q ${CONTRAXSUITE_IMAGE}:latest)
echo Contraxsuite App Docker image ID: ${CONTRAXSUITE_APP_ID}
echo ""

read -p "Enter new version to tag ContraxsuiteApp image: " -r
VERSION=${REPLY}
sudo docker tag ${CONTRAXSUITE_APP_ID} ${CONTRAXSUITE_IMAGE_FULL_NAME}:${VERSION}
sudo docker tag ${CONTRAXSUITE_APP_ID} ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest

echo ""
read -p "Are you sure to upload your local latest image to Docker registry as: ${CONTRAXSUITE_IMAGE_FULL_NAME}:${VERSION} (y/n)?" -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo docker push ${CONTRAXSUITE_IMAGE_FULL_NAME}:${VERSION}
    sudo docker push ${CONTRAXSUITE_IMAGE_FULL_NAME}:latest
fi