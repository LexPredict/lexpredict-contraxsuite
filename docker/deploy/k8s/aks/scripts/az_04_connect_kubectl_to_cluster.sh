#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd

az aks get-credentials --resource-group ${AKS_RESOURCE_GROUP} --name ${AKS_CLUSTER_NAME}
