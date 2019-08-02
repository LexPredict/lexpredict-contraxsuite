#!/bin/bash

# To be run from lexpredict-contraxsuite-services/docker dir
source setenv.sh
pushd ..
sudo ln -s $(pwd)/contraxsuite_services/media/data ${DOCKER_DIR}/volumes/contraxsuite_contraxsuite_data_media/_data

