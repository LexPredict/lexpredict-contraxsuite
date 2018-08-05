#!/bin/bash

#set -e

echo "=== This script will setup a new Contraxsuite instance"
echo ""
source setenv.sh

if [ -e ${DOCKER_DJANGO_THEME_ARCHIVE} ]
then
    echo "Theme archive found at: ${DOCKER_DJANGO_THEME_ARCHIVE}"
else
    echo "Theme archive not found at: ${DOCKER_DJANGO_THEME_ARCHIVE}"
    echo "Please copy it there first before starting the installation."
    echo "See README.md"
    exit 1
fi

if [ -e ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} ]
then
    echo "JQWidgets archive found at: ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE}"
else
    echo "JQWidgets archive not found at: ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE}"
    echo "Please copy it there first before starting the installation."
    echo "See README.md"
    exit 1
fi

echo "=== Installing Docker..." -r
pushd ./util
    source install-docker-ubuntu.sh
    source set-docker-target-dir.sh
popd
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
