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

if [[ "${CHANGE_APT_SOURCES_TO_HTTPS,,}" = 'true' ]]; then
    source ./util/change_apt_sources_to_https.sh
fi

# Assuming we are in /data/deploy/contraxsuite-deploy/docker.
# Checking if the frontend archive is in /data/deploy or in any other known location.

POSSIBLE_FRONTEND_DIRS=(
"../.."
"./deploy/dependencies"
"${HOME}"
"/tmp"
)

FRONTEND_ARCHIVE_NAME="contraxsuite-frontend.tar.gz"
FRONTEND_ARCHIVE=""
for D in "${POSSIBLE_FRONTEND_DIRS[@]}"; do
    if [[ -f "${D}/${FRONTEND_ARCHIVE_NAME}" ]]; then
        echo "Found frontend archive: ${D}/${FRONTEND_ARCHIVE_NAME}"
        ask "Do you want to use frontend from this archive?"
        if [[ ${ASK_ANSWER,,} = 'y' ]]; then
            FRONTEND_ARCHIVE="${D}/${FRONTEND_ARCHIVE_NAME}"
            break
        fi
    fi
done

if [[ "${FRONTEND_ARCHIVE}" = "" ]]; then
    echo "Frontend archive not found. To install Contraxsuite with frontend please put contraxsuite-frontend.tar.gz to one of the following dirs:"
    for D in "${POSSIBLE_FRONTEND_DIRS[@]}"; do
        echo "${D}"
    done
    echo "(paths are related to this script)"
    ask "Do you want to continue installing Contraxsuite without frontend?"
    if [[ "${ASK_ANSWER,,}" = "n" ]]; then
        exit 0
    fi
else
    echo "Unpacking ${FRONTEND_ARCHIVE} to ${VOLUME_FRONTEND}"
    sudo tar -xvf ${FRONTEND_ARCHIVE} -C ${VOLUME_FRONTEND}
fi

ask "Do you want to set up letsencrypt certs?"
if [[ ${ASK_ANSWER,,} = "y" ]]; then
    echo "=== Setting up letsencrypt certs ==="

    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install -y certbot

    sudo certbot certonly --standalone --preferred-challenges http -d ${DOCKER_DJANGO_HOST_NAME} --config-dir ./.certs
    sudo cp ./.certs/live/${DOCKER_DJANGO_HOST_NAME}/fullchain.pem ${VOLUME_NGINX_CERTS}certificate.pem
    sudo cp ./.certs/live/${DOCKER_DJANGO_HOST_NAME}/privkey.pem ${VOLUME_NGINX_CERTS}certificate.key
    sudo rm -r ./.certs

fi

echo "=== Installing Docker..."
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


echo "=== Deploying Contraxsuite stack to Docker Swarm..."
pushd ./deploy
    source deploy-contraxsuite-to-swarm-cluster.sh
popd
