#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd

az aks nodepool delete \
     --cluster-name ${AKS_CLUSTER_NAME} \
     --name rookceph \
     --resource-group ${AKS_RESOURCE_GROUP}


