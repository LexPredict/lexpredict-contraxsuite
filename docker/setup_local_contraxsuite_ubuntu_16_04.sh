#!/bin/bash

#set -e

echo "=== This script will setup a new Contraxsuite instance"
echo ""
source setenv.sh

if [ ! -f setenv_local.sh ]; then
    source init_local_env.sh
fi

source setenv_local.sh
source volumes.sh

pushd ./util/
source commons.sh
popd

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

ask "Do you want to set up letsencrypt certs?"
if [ ${ASK_ANSWER} = "y" ]; then
    echo "=== Setting up letsencrypt certs ==="

    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install -y certbot

    sudo certbot certonly --standalone --preferred-challenges http -d ${DOCKER_DJANGO_HOST_NAME} --config-dir ./.certs
    sudo cp ./.certs/live/${DOCKER_DJANGO_HOST_NAME}/fullchain.pem ${VOLUME_NGINX_CERTS}certificate.pem
    sudo cp ./.certs/live/${DOCKER_DJANGO_HOST_NAME}/privkey.pem ${VOLUME_NGINX_CERTS}certificate.key
    sudo rm -r ./.certs

    echo "=== Setting up local contraxsuite ubuntu ==="
fi

echo "=== Installing Docker..." -r
pushd ./util
    source install-docker-ubuntu.sh
    source set-docker-target-dir.sh
echo ""

echo "=== Creating user shared between Docker containers and host machine..."
source install-docker-shared-user.sh

echo "=== Initializing Docker Swarm cluster..."
set -e
source install-docker-swarm.sh
set +e
popd


if [ ! -z "${DISTR_DOCKER_IMAGE_URL}" ]; then
    echo "=== Downloading Contraxsuite image from dist server"
    rm -f ./image.tar
    apt-get update
    apt-get -y install axel
    axel --num-connections=5 ${DISTR_DOCKER_IMAGE_URL} -o ./image.tar
    sudo docker load < image.tar
    rm -f ./image.tar

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
