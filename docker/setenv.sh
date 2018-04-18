#!/bin/bash

export CONTRAXSUITE_ROOT=../contraxsuite_services

export DOCKER_HOST_NAME_PG=contrax-db
export DOCKER_HOST_NAME_REDIS=contrax-redis
export DOCKER_HOST_NAME_RABBITMQ=contrax-rabbitmq
# Host name for Elastic should not contain underscores. Logstash crashes if seeing them in ES URL.
export DOCKER_HOST_NAME_ELASTICSEARCH=contrax-elasticsearch
export DOCKER_HOST_NAME_UWSGI=contrax-uwsgi
export DOCKER_HOST_NAME_KIBANA=contrax-kibana

export DOCKER_PG_USER=contrax1
export DOCKER_PG_PASSWORD=contrax1
export DOCKER_PG_DB_NAME=contrax1

export DOCKER_RABBITMQ_VHOST=contrax1_vhost
export DOCKER_RABBITMQ_USER=contrax1
export DOCKER_RABBITMQ_PASSWORD=contrax1

export DOCKER_JUPYTER_BASE_URL=/jupyter
export DOCKER_JUPYTER_PORT=8888

export DOCKER_KIBANA_BASE_PATH=


export DOCKER_DJANGO_HOST_NAME=localhost
export DOCKER_DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
export DOCKER_DJANGO_EMAIL_HOST=localhost
# Base path should start and end with slashes
export DOCKER_DJANGO_BASE_PATH=/
export DOCKER_DJANGO_EMAIL_USE_TLS=False
export DOCKER_DJANGO_EMAIL_PORT=587
export DOCKER_DJANGO_EMAIL_HOST_USER=
export DOCKER_DJANGO_EMAIL_HOST_PASSWORD=
export DOCKER_DJANGO_ADMIN_NAME=Administrator
export DOCKER_DJANGO_ADMIN_PASSWORD=Administrator
export DOCKER_DJANGO_ADMIN_EMAIL=admin@localhost
export DOCKER_DJANGO_DEBUG=False
export DOCKER_DJANGO_DEBUG_SQL=False
export DOCKER_DJANGO_SECRET_KEY=Welcome1
export DOCKER_DJANGO_ACCOUNT_EMAIL_VERIFICATION=optional
export DOCKER_DJANGO_THEME_ARCHIVE=./deploy/dependencies/theme-example.zip
export DOCKER_DJANGO_JQWIDGETS_ARCHIVE=./deploy/dependencies/jqwidgets-example.zip
export DOCKER_VOLUME_DIR=/var/lib/docker/volumes

export DOCKER_NGINX_SERVER_NAME=localhost
export DOCKER_NGINX_CERTIFICATE=
export DOCKER_NGINX_CERTIFICATE_KEY=

export SHARED_USER_ID=65432
export SHARED_USER_NAME=contraxsuite_docker_user

export DOCKER_REGISTRY=
export DOCKER_USERNAME=
export CONTRAXSUITE_IMAGE=lexpredict/lexpredict-contraxsuite

export DOCKER_CELERY_CPUS=1
export DOCKER_CELERY_MEMORY=4G
export DOCKER_POSTGRES_CPUS=1
export DOCKER_POSTGRES_MEMORY=4G
export DOCKER_JUPYTER_CPUS=1
export DOCKER_JUPYTER_MEMORY=4G
export DOCKER_ELASTICSEARCH_CPU=1
export DOCKER_ELASTICSEARCH_MEMORY=4G
export DOCKER_TIKA_CPU=1
export DOCKER_TIKA_MEMORY=4G


if [ -e setenv_local.sh ]
then
    source setenv_local.sh
fi

if [ -z "${DOCKER_REGISTRY}" ]; then
    if [ ! -z "${DOCKER_USERNAME}" ]; then
        export CONTRAXSUITE_IMAGE_FULL_NAME=${DOCKER_USERNAME}/${CONTRAXSUITE_IMAGE}
    else
        export CONTRAXSUITE_IMAGE_FULL_NAME=${CONTRAXSUITE_IMAGE}
    fi
else
    export CONTRAXSUITE_IMAGE_FULL_NAME=${DOCKER_REGISTRY}/${CONTRAXSUITE_IMAGE}
fi


