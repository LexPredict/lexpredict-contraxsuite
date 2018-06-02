#!/bin/bash
set -e

pushd ../../

source setenv.sh

popd

sudo -E docker stack deploy --compose-file docker-compose.yml contraxsuite_registry
