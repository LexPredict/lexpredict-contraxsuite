#!/bin/bash
set -e

pushd ../../

source setenv.sh

popd

sudo -E docker stack rm contraxsuite_registry

sleep 10

sudo -E ls -l ${DOCKER_VOLUME_DIR}/contraxsuite_registry_registry_storage/_data/docker | echo "Volume dir does not exist"

sudo -E rm -rf ${DOCKER_VOLUME_DIR}/contraxsuite_registry_registry_storage/_data/docker

sudo -E ls -l ${DOCKER_VOLUME_DIR}/contraxsuite_registry_registry_storage/_data/docker | echo "Volume dir does not exist"

source deploy-registry.sh

sleep 5