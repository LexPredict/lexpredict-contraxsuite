#!/bin/bash
set -e

pushd ../../
source setenv.sh
popd

echo "Image name: ${CONTRAXSUITE_IMAGE}"
export DOLLAR='$' # escape $ in envsubst

envsubst < Dockerfile.template > Dockerfile

# Docker is not allowed to access files in the parent dir
# Preparing files in a temp dir
rm -f -r ./temp
mkdir -p ./temp

echo "">./temp/python-requirements-additional.txt
if [ -e ../../../python-requirements-additional.txt ]
then
    cat ../../../python-requirements-additional.txt>>./temp/python-requirements-additional.txt
fi


mkdir -p ./temp/contraxsuite_services
mkdir -p ./temp/static
mkdir -p ./temp/additionals
mkdir -p ./temp/ssl_certs

mkdir -p ../../../additionals
mkdir -p ../../../ssl_certs

# Build tika jars into contraxsuite_services/jars
# Next they will be copied into the image together with contraxsuite_services folder
echo "Building Tika jars"
pushd ../../../scripts
rm -f ../contraxsuite_services/jars/* || true

sudo -E ./obtain_jars.sh

popd



echo "Contraxsuite additional files" > ../../../additionals/additionals
rsync --exclude='.git/' --exclude='lexnlpprivate/' ../../../additionals/ ./temp/additionals/ -a --copy-links -v

echo "Contraxsuite custom SSL certificates" > ../../../ssl_certs/ssl_certs
rsync --exclude='.git/' ../../../ssl_certs/ ./temp/ssl_certs/ -a --copy-links -v

rsync --exclude='.git/' ../../../contraxsuite_services/ ./temp/contraxsuite_services/ -a --copy-links -v
rsync --exclude='.git/' ../../../static/ ./temp/static/ -a --copy-links -v

# Don't put licensed third-party components into the image
rm -f -r ./temp/contraxsuite_services/staticfiles
rm -f ./temp/contraxsuite_services/local_settings.py
rm -f ./temp/contraxsuite_services/uwsgi.ini
rm -r ./temp/static/vendor/jqwidgets

echo "LexPredict Contraxsuite App Docker Image" > ./temp/build.info
echo "Built at: $(uname -a)" >> ./temp/build.info
echo "Build date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> ./temp/build.info

# Generate build uid used for understanding if the persistent static files need to be updated
uuidgen>./temp/build.uuid

sudo docker build ${DOCKER_BUILD_FLAGS} --no-cache -t ${CONTRAXSUITE_IMAGE} .
# sudo docker build --no-cache -t contraxsuite-app .

rm -f -r ./temp

rm -f -r Dockerfile
