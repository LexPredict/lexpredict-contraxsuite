#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

az aks get-versions -l ${AKS_CLUSTER_LOCATION}
