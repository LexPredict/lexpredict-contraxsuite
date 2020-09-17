#!/bin/bash

export SUPPORT_EMAIL=support@lexpredict.com

export AKS_RESOURCE_GROUP=
export AKS_CLUSTER_NAME=


export AKS_CLUSTER_LOCATION=eastus2
export AKS_CLUSTER_K8S_VERSION=1.16.10
export AKS_CLUSTER_NODE_COUNT=3
export AKS_CLUSTER_NODE_OS_DISK_SIZE=150
export AKS_CLUSTER_NODE_VM_SIZE=Standard_D8s_v3
export AKS_CLUSTER_MIN_COUNT=3
export AKS_CLUSTER_MAX_COUNT=20

export PROMETHEUS_NAMESPACE=prometheus
export PROMETHEUS_NGINX_HELM_RELEASE_NAME=nginx
export GRAFANA_DOMAIN_NAME=

export GRAFANA_ADD_CLOUDFLARE_DNS=yes
export CLOUDFLARE_DNS_URL=
export CLOUDFLARE_DNS_AUTHORIZATION=

export GRAFANA_ADD_LETSENCRYPT_CERT=yes


export CEPH_NODE_POOL_NAME=rookceph
export CEPH_NODE_COUNT=3

export CONTRAXSUITE_NAMESPACE=
export DOCKERHUB_USERNAME=



if [ -f setenv_local.sh ]
then
    echo "Loading setenv_local.sh"
    source aks_setenv_local.sh
fi