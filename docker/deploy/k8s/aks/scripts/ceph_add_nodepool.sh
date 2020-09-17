#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd

az aks nodepool add \
     --cluster-name ${AKS_CLUSTER_NAME} \
     --name rookceph \
     --resource-group ${AKS_RESOURCE_GROUP} \
     --node-count 3 \
     --node-taints storage-node=true:NoSchedule

