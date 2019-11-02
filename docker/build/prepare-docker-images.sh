#!/bin/bash
set -e
pushd ../
source setenv.sh
popd

pushd contraxsuite-app
./prepare-image-app.sh
popd
