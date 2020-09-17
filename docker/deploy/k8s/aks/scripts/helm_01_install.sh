#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

rm -rf /tmp/install_helm
mkdir -p /tmp/install_helm
pushd /tmp/install_helm > /dev/null

curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh

popd > /dev/null
rm -rf /tmp/install_helm


echo "Need to sleep a bit to make helm finish its installation..."
sleep 30
