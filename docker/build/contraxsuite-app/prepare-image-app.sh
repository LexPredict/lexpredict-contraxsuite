#!/bin/bash
set -e

source ../../setenv.sh
if [ -e ../../setenv_local.sh ]
then
    source ../../setenv_local.sh
fi

echo "Image name: ${CONTRAXSUITE_IMAGE}"
export DOLLAR='$' # escape $ in envsubst

# Docker is not allowed to access files in the parent dir
# Preparing files in a temp dir
rm -f -r ./temp
mkdir -p ./temp

echo "">./temp/python-requirements-additional.txt
if [ -e ../../../python-requirements-additional.txt ]
then
    cat ../../../python-requirements-additional.txt>>./temp/python-requirements-additional.txt
fi

mkdir -p ../../../additionals
cp -r ../../../additionals ./temp/


cp -r ../../../contraxsuite_services ./temp/
cp -r ../../../static ./temp/

# Don't put licensed third-party components into the image
rm -f -r ./temp/contraxsuite_services/staticfiles
rm -f ./temp/contraxsuite_services/local_settings.py
rm -r ./temp/static/theme
rm -r ./temp/static/vendor/jqwidgets

echo "LexPredict Contraxsuite App Docker Image" > ./temp/build.info
echo "Built at: $(uname -a)" >> ./temp/build.info
echo "Build date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> ./temp/build.info

# Generate build uid used for understanding if the persistent static files need to be updated
uuidgen>./temp/build.uuid

sudo docker build -t ${CONTRAXSUITE_IMAGE} .
# sudo docker build --no-cache -t contraxsuite-app .

rm -f -r ./temp
