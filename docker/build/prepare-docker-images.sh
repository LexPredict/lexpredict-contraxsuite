#!/bin/bash
set -e
source ../setenv.sh
if [ -e ../setenv_local.sh ]
then
    source ../setenv_local.sh
fi

pushd contraxsuite-app
./prepare-image-app.sh
popd
