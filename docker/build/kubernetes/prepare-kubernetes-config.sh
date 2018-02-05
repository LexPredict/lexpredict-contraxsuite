#!/bin/bash

TEMP_DIR=./kubernetes-temp

rm -r ${TEMP_DIR}
mkdir -p ${TEMP_DIR}

pushd ${TEMP_DIR}

# Kompose is at https://github.com/kubernetes/kompose
kompose convert -f ../../../deploy/docker-compose.yml
find . -type f | (while read line; do cat $line; echo ""; echo "---"; echo ""; done;) > ../contraxsuite-kubernetes.yaml

popd
rm -r ${TEMP_DIR}