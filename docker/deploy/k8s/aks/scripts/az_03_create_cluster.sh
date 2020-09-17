#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

set +e

az group create \
    --location ${AKS_CLUSTER_LOCATION} \
    --name ${AKS_RESOURCE_GROUP}

az aks create \
    -g ${AKS_RESOURCE_GROUP} \
    -n ${AKS_CLUSTER_NAME} \
    --location ${AKS_CLUSTER_LOCATION} \
    --kubernetes-version ${AKS_CLUSTER_K8S_VERSION} \
    --node-count ${AKS_CLUSTER_NODE_COUNT} \
    --node-osdisk-size ${AKS_CLUSTER_NODE_OS_DISK_SIZE} \
    --node-vm-size ${AKS_CLUSTER_NODE_VM_SIZE} \
    --vm-set-type VirtualMachineScaleSets \
    --enable-cluster-autoscaler \
    --min-count ${AKS_CLUSTER_MIN_COUNT} \
    --max-count ${AKS_CLUSTER_MAX_COUNT}
