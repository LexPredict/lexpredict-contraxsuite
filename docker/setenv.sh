#!/bin/bash

export CPU_CORES=$(grep -c ^processor /proc/cpuinfo)
export CPU_HALF_CORES=$(( ${CPU_CORES} / 2 ))
export CPU_QUARTER_CORES=$(( ${CPU_CORES} / 4 ))
export RAM_MB=$(( $(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 ))
export RAM_HALF_MB=$(( ${RAM_MB} / 2 ))
export RAM_QUARTER_MB=$(( ${RAM_MB} / 4 ))

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
export DOCKER_PG_MAX_BACKUP_NUMBER=3

export DOCKER_RABBITMQ_VHOST=contrax1_vhost
export DOCKER_RABBITMQ_USER=contrax1
export DOCKER_RABBITMQ_PASSWORD=contrax1

export DOCKER_JUPYTER_BASE_URL=/jupyter
export DOCKER_JUPYTER_HOST_NAME=contrax-jupyter
export DOCKER_JUPYTER_PORT=8888

export DOCKER_KIBANA_BASE_PATH=/kibana


export DOCKER_DJANGO_HOST_NAME=localhost
export DOCKER_DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
export DOCKER_DJANGO_EMAIL_HOST=localhost
# Base path should start and end with slashes
export DOCKER_DJANGO_BASE_PATH=/advanced/
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
export DOCKER_DJANGO_THEME_ARCHIVE=./deploy/dependencies/theme.zip
export DOCKER_DJANGO_JQWIDGETS_ARCHIVE=./deploy/dependencies/jqwidgets.zip
export DOCKER_DIR=/data/docker

export DOCKER_NGINX_SERVER_NAME=contrax-nginx
export DOCKER_NGINX_CERTIFICATE=
export DOCKER_NGINX_CERTIFICATE_KEY=
export DOCKER_NGINX_CORS_CONFIG=cors_disable
export DOCKER_NGINX_CPU_RESERVATIONS=0.5
export DOCKER_NGINX_MEMORY_RESERVATIONS=512M

export DOCKER_FLOWER_BASE_PATH=flower
export DOCKER_HOST_NAME_FLOWER=contrax-flower

export SHARED_USER_ID=65432
export SHARED_USER_NAME=contraxsuite_docker_user

export DOCKER_REGISTRY=
export CONTRAXSUITE_IMAGE=lexpredict/lexpredict-contraxsuite

export DOCKER_CELERY_CPUS=4
export DOCKER_CELERY_MEMORY=8G
export DOCKER_UWSGI_MEMORY=8G
export DOCKER_UWSGI_CPU_RESERVATIONS=2
export DOCKER_UWSGI_MEMORY_RESERVATIONS=2G
export DOCKER_CELERY_BEAT_CPUS=2
export DOCKER_CELERY_BEAT_MEMORY=4G
export DOCKER_CELERY_MASTER_CPUS=2
export DOCKER_CELERY_MASTER_MEMORY=4G

export DOCKER_POSTGRES_CPUS=4
export DOCKER_POSTGRES_MEMORY=6G
export DOCKER_POSTGRES_CPU_RESERVATIONS=1
export DOCKER_POSTGRES_MEMORY_RESERVATIONS=2G
export DOCKER_JUPYTER_CPUS=1
export DOCKER_JUPYTER_MEMORY=4G
export DOCKER_FLOWER_CPUS=1
export DOCKER_FLOWER_MEMORY=2G
export DOCKER_ELASTICSEARCH_CPU=2
export DOCKER_ELASTICSEARCH_MEMORY=4G
export DOCKER_TIKA_CPU=2
export DOCKER_TIKA_MEMORY=4G

export DISTR_DOCKER_IMAGE_URL=
export DISTR_DOCKER_IMAGE_NAME=
export DISTR_DEPLOY_SCRIPTS_URL=
export DISTR_USER=
export DISTR_PASSWORD=


export DOCKER_BUILD_FLAGS=

export PG_STATISTICS_ENABLED=false

#export DOCKER_COMPOSE_FILE=docker-compose-single-master-many-workers.yml
export DOCKER_COMPOSE_FILE=docker-compose-single-host.yml

export DOCKER_SWARM_ADVERTISE_ADDR=


if [ -f setenv_distr.sh ]
then
    echo "Loading setenv_distr.sh"
    source setenv_distr.sh
fi

if [ -f setenv_local.sh ]
then
    echo "Loading setenv_local.sh"
    source setenv_local.sh
fi

if [ -z "${DOCKER_REGISTRY}" ]; then
    export CONTRAXSUITE_IMAGE_FULL_NAME=${CONTRAXSUITE_IMAGE}
else
    export CONTRAXSUITE_IMAGE_FULL_NAME=${DOCKER_REGISTRY}/${CONTRAXSUITE_IMAGE}
fi
