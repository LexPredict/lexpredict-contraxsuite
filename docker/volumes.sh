#!/usr/bin/env bash

source setenv.sh
if [ -e ../setenv_local.sh ]
then
    source setenv_local.sh
fi

export VOLUME_NGINX_CONF=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_nginx_conf/_data/
export VOLUME_NGINX_CERTS=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_nginx_certs/_data/
export VOLUME_FRONTEND=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_frontend/_data/
export VOLUME_THIRD_PARTY=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_third_party_dependencies/_data/

# Initialize volumes
sudo mkdir -p ${VOLUME_NGINX_CONF}
sudo mkdir -p ${VOLUME_NGINX_CERTS}
sudo mkdir -p ${VOLUME_NGINX_CONF}/conf.d
sudo mkdir -p ${VOLUME_FRONTEND}
sudo mkdir -p ${VOLUME_THIRD_PARTY}
