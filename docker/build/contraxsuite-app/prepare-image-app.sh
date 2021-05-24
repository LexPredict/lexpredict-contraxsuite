#!/bin/bash
set -e

pushd ../
source build_setenv.sh
popd

echo "Image name: ${CONTRAXSUITE_IMAGE}"
export DOLLAR='$' # escape $ in envsubst

# Docker is not allowed to access files in the parent dir
# Preparing files in a temp dir
rm -f -r ./temp
mkdir -p ./temp


if [[ "${INSTALL_LEXNLP_MASTER,,}" = "true" ]]; then
    export LEXNLP_MASTER_INSTALL_CMD="&& pip3 install -r /contraxsuite_services/deploy/base/python-requirements-lexnlp.txt"
else
    export LEXNLP_MASTER_INSTALL_CMD=""
fi

if [[ "${TEXT_EXTRACTION_INSTALL_MASTER,,}" = "true" ]]; then
    export TEXT_EXTRACTION_API_INSTALL_CMD="&& pip3 install -r /contraxsuite_services/deploy/base/python-requirements-text-extraction.txt"
else
    export TEXT_EXTRACTION_API_INSTALL_CMD=
fi

envsubst < Dockerfile.template > Dockerfile

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

echo "Contraxsuite additional files" > ../../../additionals/additionals
rsync --exclude='.git/' --exclude='lexnlpprivate/' ../../../additionals/ ./temp/additionals/ -a --copy-links -v

echo "Contraxsuite custom SSL certificates" > ../../../ssl_certs/ssl_certs
rsync --exclude='.git/' ../../../ssl_certs/ ./temp/ssl_certs/ -a --copy-links -v

rsync --exclude='.git/' ../../../contraxsuite_services/ ./temp/contraxsuite_services/ -a --copy-links -v
rsync --exclude='.git/' ../../../static/ ./temp/static/ -a --copy-links -v

rm -f -r ./temp/contraxsuite_services/staticfiles
rm -f ./temp/contraxsuite_services/local_settings.py
rm -f ./temp/contraxsuite_services/uwsgi.ini
rm -f ./temp/additionals/additionals

sed -i "/VERSION_NUMBER/ c\VERSION_NUMBER = '${CONTRAXSUITE_VERSION}'" ./temp/contraxsuite_services/settings.py
sed -i "/VERSION_COMMIT/ c\VERSION_COMMIT = '${BUILD_CONTRAXSUITE_GIT_COMMIT}'" ./temp/contraxsuite_services/settings.py



echo "LexPredict Contraxsuite App Docker Image" > ./temp/build.info
echo "Built at: $(uname -a)" >> ./temp/build.info
echo "Build date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> ./temp/build.info

# Generate build uid used for understanding if the persistent static files need to be updated
uuidgen>./temp/build.uuid
envsubst < start.template.sh > ./temp/start.sh

sudo DOCKER_BUILDKIT=1 docker build ${DOCKER_BUILD_FLAGS} --no-cache -t ${CONTRAXSUITE_IMAGE} .
# sudo docker build --no-cache -t contraxsuite-app .

rm -f -r ./temp

rm -f -r Dockerfile
