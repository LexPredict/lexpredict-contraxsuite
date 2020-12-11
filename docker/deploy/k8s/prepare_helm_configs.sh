#!/bin/bash

# This script prepares Helm files.
# Should be executed from the dir in which it persists. Example: cd docker/deploy/k8s && ./prepare_helm_configs.sh

pushd ../../ > /dev/null
source setenv.sh
popd > /dev/null

source helm_setenv.sh

pushd ../ > /dev/null
source prepare_configs.sh
popd

# # Find each occurrence of readconfig string in configmap, remove readconfig_ prefix and replace with an appropriate config template file
# cp contraxsuite/templates/configmap.template.yaml contraxsuite/templates/configmap.yaml

# grep readconfig contraxsuite/templates/configmap.yaml | while read -r line ; do
#     line=${line//readconfig_/}
#     echo "Processing: $line"
#     if [[ -z $(head -n 1 ../temp/$line | egrep -n "^\s") ]]; then
#         sed -i -e 's/^/    /' ../temp/$line
#     fi
#     sed -i -e "/readconfig_$line/{r ../temp/$line" -e 'd}' contraxsuite/templates/configmap.yaml
# done

env
envsubst < ./contraxsuite/Chart.template.yaml > ./contraxsuite/Chart.yaml
envsubst < ./contraxsuite/values.template.yaml > ./contraxsuite/values.yaml