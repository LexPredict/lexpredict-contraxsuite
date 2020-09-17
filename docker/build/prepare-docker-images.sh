#!/bin/bash
set -e
source build_setenv.sh

pushd contraxsuite-app
./prepare-image-app.sh
popd
