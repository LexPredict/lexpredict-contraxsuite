#!/bin/bash
set -e

pushd ../

source setenv.sh

VOLUME=/var/lib/docker/volumes/contraxsuite_contraxsuite_third_party_dependencies/_data/
sudo mkdir -p ${VOLUME}
sudo cp ${DOCKER_DJANGO_THEME_ARCHIVE} ${VOLUME}
sudo cp ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} ${VOLUME}
sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME}

if [ ! -z ${DOCKER_NGINX_CERTIFICATE} ]; then
    VOLUME=/var/lib/docker/volumes/contraxsuite_contraxsuite_nginx_certs/_data/
    sudo mkdir -p ${VOLUME}
    sudo cp ${DOCKER_NGINX_CERTIFICATE} ${VOLUME}/certificate.pem
    sudo cp ${DOCKER_NGINX_CERTIFICATE_KEY} ${VOLUME}/certificate.key
    sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME}
fi

popd
sudo -E docker stack deploy --compose-file docker-compose.yml contraxsuite
#docker-compose run contrax_rabbitmq
