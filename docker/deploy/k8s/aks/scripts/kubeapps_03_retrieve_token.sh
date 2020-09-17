#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd

set -e

echo "Retrieving token for kubeapps..."
kubectl get secret $(kubectl get serviceaccount kubeapps-operator -o jsonpath='{.secrets[].name}') -o jsonpath='{.data.token}' | base64 --decode && echo