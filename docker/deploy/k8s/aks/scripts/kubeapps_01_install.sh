#!/bin/bash

pushd .. > /dev/null
source aks_setenv.sh
popd

set -e
echo "Installing kubeapps..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install --name kubeapps --namespace kubeapps bitnami/kubeapps

echo "Creating service account for kubeapps..."
kubectl create serviceaccount kubeapps-operator
kubectl create clusterrolebinding kubeapps-operator --clusterrole=cluster-admin --serviceaccount=default:kubeapps-operator

./aks_kubeapps_03_retrieve_token.sh
