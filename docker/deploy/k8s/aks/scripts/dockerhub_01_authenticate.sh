#!/bin/bash

pushd .. > /dev/null
source aks_setenv.sh
popd

kubectl create namespace ${CONTRAXSUITE_NAMESPACE}

echo "Enter dockerhub password for Docker ID ${DOCKERHUB_USERNAME}: "
read -s DOCKERHUB_PASSWORD

kubectl create secret docker-registry contraxsuitesecret \
	--docker-server=https://index.docker.io/v1/ \
	--docker-username=${DOCKERHUB_USERNAME} \
	--docker-password=${DOCKERHUB_PASSWORD} \
	-n ${CONTRAXSUITE_NAMESPACE}


