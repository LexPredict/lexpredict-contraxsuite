#!/bin/bash

export CONTRAXSUITE_ROOT=../contraxsuite_services

export DOCKER_HOST_NAME_PG=contrax_db
export DOCKER_HOST_NAME_REDIS=contrax_redis
export DOCKER_HOST_NAME_RABBITMQ=contrax_rabbitmq
export DOCKER_HOST_NAME_ELASTICSEARCH=contrax_elasticsearch
export DOCKER_HOST_NAME_UWSGI=contrax_uwsgi

export DOCKER_PG_USER=contrax1
export DOCKER_PG_PASSWORD=contrax1
export DOCKER_PG_DB_NAME=contrax1

export DOCKER_RABBITMQ_VHOST=contrax1_vhost
export DOCKER_RABBITMQ_USER=contrax1
export DOCKER_RABBITMQ_PASSWORD=contrax1


export DOCKER_DJANGO_HOST_NAME=localhost
export DOCKER_DJANGO_EMAIL_HOST=localhost
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

export DOCKER_NGINX_SERVER_NAME=localhost
export DOCKER_NGINX_CERTIFICATE=
export DOCKER_NGINX_CERTIFICATE_KEY=

export SHARED_USER_ID=65432
export SHARED_USER_NAME=contraxsuite_docker_user

export DOCKER_REGISTRY=$(hostname):5001
export DOCKER_USERNAME=
export CONTRAXSUITE_IMAGE=contraxsuite-app


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


