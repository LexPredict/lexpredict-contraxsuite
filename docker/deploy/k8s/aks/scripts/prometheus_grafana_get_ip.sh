#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

NGINX_EXTERNAL_IP=$(kubectl get services --namespace ${PROMETHEUS_NAMESPACE} ${PROMETHEUS_NGINX_HELM_RELEASE_NAME}-nginx-ingress-controller --output jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "${GRAFANA_DOMAIN_NAME} should lead to ${NGINX_EXTERNAL_IP}"

nslookup ${GRAFANA_DOMAIN_NAME}
