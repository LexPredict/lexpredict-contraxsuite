#!/bin/bash

export CONTRAXSUITE_IMAGE=lexpredict/lexpredict-contraxsuite:latest
export CONTRAXSUITE_VERSION=0.0.0
export CONTRAXSUITE_IMAGE_FROM=ubuntu:18.04
export SHARED_USER_ID=65432
export SHARED_USER_NAME=contraxsuite_docker_user
export DOCKER_BUILD_FLAGS=

export BUILD_CONTRAXSUITE_GIT_COMMIT=unknown

export INSTALL_LEXNLP_MASTER=true


if [ -f build_setenv_local.sh ]
then
    echo "Loading build_setenv_local.sh"
    source build_setenv_local.sh
fi
