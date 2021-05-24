#!/bin/bash

export HELM_CHART_APP_VERSION=develop
export HELM_CHART_VERSION=0.0.0

export DOCKER_DJANGO_HOST_NAME="{{ .Values.domain_name }}"
export DOCKER_FRONTEND_ROOT_URL="{{ .Values.domain_name }}"

# Rewrite DOCKER_TEXT_EXTRACTION_SYSTEM_URL for K8S
export DOCKER_TEXT_EXTRACTION_SYSTEM_URL=http://${DOCKER_HOST_NAME_TEXT_EXTRACTION_SYSTEM_API}:${DOCKER_TEXT_EXTRACTION_SYSTEM_API_PORT}

if [[ -f helm_setenv_local.sh ]]; then
    echo "Loading helm_setenv_local.sh"
    source helm_setenv_local.sh
fi
