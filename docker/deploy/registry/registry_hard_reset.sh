#!/bin/bash
set -e

pushd ../../

source volumes.sh

popd

sudo -E docker stack rm contraxsuite_registry

sleep 20

sudo -E ls -l ${VOLUME_REGISTRY}/docker | echo "Volume dir does not exist"

sudo -E rm -rf ${VOLUME_REGISTRY}/docker

sudo -E ls -l ${VOLUME_REGISTRY}/docker | echo "Volume dir does not exist"

source deploy-registry.sh

sleep 5
