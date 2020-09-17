#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd

set -e

echo "Creating service account"
kubectl create serviceaccount -n kube-system tiller

echo "Creating cluster role binding"
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

echo "Running helm init..."
helm init --service-account tiller

