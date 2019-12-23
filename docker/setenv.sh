#!/bin/bash

export CPU_CORES=$(grep -c ^processor /proc/cpuinfo)
export CPU_HALF_CORES=$(( ${CPU_CORES} / 2 ))
export CPU_QUARTER_CORES=$(( ${CPU_CORES} / 4 ))
export RAM_MB=$(( $(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 ))
export RAM_HALF_MB=$(( ${RAM_MB} / 2 ))
export RAM_QUARTER_MB=$(( ${RAM_MB} / 4 ))

export POSTGRES_CPUS=$(( 4*${CPU_CORES}/5  ))
export POSTGRES_RAM=$(( 3*${RAM_MB}/4  ))
export POSTGRES_MAX_CONNECTIONS=1000
export POSTGRES_SHARED_BUFFERS=$(( ${POSTGRES_RAM}/4 ))MB
export POSTGRES_EFFECTIVE_CACHE_SIZE=$(( 3*${POSTGRES_RAM}/4 ))MB
export POSTGRES_MAINTENANCE_WORK_MEM=$(( ${POSTGRES_RAM}/16 ))MB

export POSTGRES_DISK=hdd

if [[ ${POSTGRES_DISK} = "ssd" ]]; then
    export POSTGRES_RANDOM_PAGE_COST=1.1
    export POSTGRES_EFFECTIVE_IO_CONCURRENCY=200
else
    export POSTGRES_RANDOM_PAGE_COST=4
    export POSTGRES_EFFECTIVE_IO_CONCURRENCY=2
fi

export POSTGRES_PARALLEL_WORKERS_PER_GATHER=$(( (${POSTGRES_CPUS}+2-1)/2 ))  # ceil (cpus / 2)

# ((RAM - shared_buffers) / (max_connections * 3) / max_parallel_workers_per_gather)
# + some magic
export POSTGRES_WORK_MEM=$(( 3*1024*${POSTGRES_RAM}/(2*4*${POSTGRES_MAX_CONNECTIONS}*3*((${POSTGRES_CPUS}+2-1)/2))  ))kB


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
export DOCKER_DJANGO_BASE_PATH_STRIPPED=${DOCKER_DJANGO_BASE_PATH%/}
export DOCKER_DJANGO_EMAIL_USE_TLS=False
export DOCKER_DJANGO_EMAIL_PORT=587
export DOCKER_DJANGO_EMAIL_HOST_USER=
export DOCKER_DJANGO_EMAIL_HOST_PASSWORD=
export DOCKER_DJANGO_ADMIN_NAME=Administrator
export DOCKER_DJANGO_ADMIN_PASSWORD=Administrator
export DOCKER_DJANGO_ADMIN_EMAIL=admin@localhost
export DOCKER_DJANGO_DEBUG=False
export DOCKER_DJANGO_DEBUG_SQL=False

# use django's builtin method to create a key eithe any random string
# >>> from django.core.management.utils import get_random_secret_key
# >>> get_random_secret_key()
export DOCKER_DJANGO_SECRET_KEY=Welcome1
export DOCKER_DJANGO_ACCOUNT_EMAIL_VERIFICATION=optional
export DOCKER_DJANGO_JQWIDGETS_ARCHIVE=./deploy/dependencies/jqwidgets.zip
export DOCKER_DIR=/data/docker

export DOCKER_NGINX_SERVER_NAME=contrax-nginx
export DOCKER_NGINX_CERTIFICATE=
export DOCKER_NGINX_CERTIFICATE_KEY=
export DOCKER_NGINX_CORS_CONFIG=cors_disable
export DOCKER_NGINX_CPU_RESERVATIONS=0.5
export DOCKER_NGINX_MEMORY_RESERVATIONS=512M

export DOCKER_WEBDAV_SERVER_NAME=contrax-webdav
export DOCKER_WEBDAV_AUTH_USER=user
export DOCKER_WEBDAV_AUTH_PASSWORD=password

export DOCKER_FLOWER_BASE_PATH=flower
export DOCKER_HOST_NAME_FLOWER=contrax-flower
export FLOWER_REPLICAS=0

# This is required to be the same user id as WebDAV storage reads/writes with.
# For bytemark/webdav:2.4 its id is 82
export SHARED_USER_ID=82

export SHARED_USER_NAME=contraxsuite_docker_user

export SHARED_USER_LOG_READER_ID=65431
export SHARED_USER_LOG_READER_NAME=contraxsuite_docker_log_reader


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

export DOCKER_JUPYTER_CPUS=$(( ${CPU_CORES}/5  ))
export DOCKER_JUPYTER_MEMORY=$(( ${RAM_MB}/5  ))M
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

export PG_STATISTICS_ENABLED=true

#export DOCKER_COMPOSE_FILE=docker-compose-single-master-many-workers.yml
export DOCKER_COMPOSE_FILE=docker-compose-single-host.yml

export DOCKER_SWARM_ADVERTISE_ADDR=

export CONTRAXSUITE_IMAGE_VERSION=latest

export LEXNLP_TIKA_PARSER_MODE=pdf_ocr


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

export DOCKER_FRONTEND_ROOT_URL=${DOCKER_DJANGO_HOST_NAME}

if [ -z "${DOCKER_REGISTRY}" ]; then
    export CONTRAXSUITE_IMAGE_FULL_NAME=${CONTRAXSUITE_IMAGE}
else
    export CONTRAXSUITE_IMAGE_FULL_NAME=${DOCKER_REGISTRY}/${CONTRAXSUITE_IMAGE}
fi

export DOCKER_POSTGRES_LOG_MIN_DUR_STMT=-1
