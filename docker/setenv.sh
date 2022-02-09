#!/bin/bash

export DOLLAR='$' # escape $ in envsubst

export WITH_JS_FRONTEND=false
export WITH_HTTPS=false

export CHANGE_APT_SOURCES_TO_HTTPS=true

export DOCKER_NGINX_IMAGE=nginx:1.16.1
export DOCKER_PG_IMAGE=postgres:11.5
export DOCKER_REDIS_IMAGE=redis:5-alpine
export DOCKER_WEBDAV_IMAGE=bytemark/webdav:2.4
export DOCKER_MINIO_IMAGE=minio/minio:RELEASE.2020-01-03T19-12-21Z
export DOCKER_MLFLOW_TRACKING_IMAGE=lexpredict/mlflow-tracking-server:1.6.0-1
export DOCKER_CURATOR_IMAGE=lexpredict/es-curator-cron:5.8.1-1
export DOCKER_ELASTICSEARCH_IMAGE=elasticsearch:7.16.2
export DOCKER_ELASTALERT_IMAGE=bitsensor/elastalert:3.0.0-beta.1
export DOCKER_KIBANA_IMAGE=lexpredict/lexpredict-kibana:7.16.2
export DOCKER_FILEBEAT_IMAGE=elastic/filebeat:7.16.2
export DOCKER_METRICBEAT_IMAGE=elastic/metricbeat:7.16.2
export DOCKER_RABBITMQ_IMAGE=rabbitmq:3.8-management
export DOCKER_PGBOUNCER_IMAGE=edoburu/pgbouncer:1.15.0

export MOCK_IMANAGE_REPLICAS=0


export CPU_CORES=$(grep -c ^processor /proc/cpuinfo)
export CPU_HALF_CORES=$(( ${CPU_CORES} / 2 ))
export CPU_QUARTER_CORES=$(( ${CPU_CORES} / 4 ))
export RAM_MB=$(( $(awk '/MemTotal/ {print $2}' /proc/meminfo) / 1024 ))
export RAM_HALF_MB=$(( ${RAM_MB} / 2 ))
export RAM_QUARTER_MB=$(( ${RAM_MB} / 4 ))

export POSTGRES_ENABLE_DAILY_REINDEX=true
export POSTGRES_CPUS=$(( 4*${CPU_CORES}/5  ))
export POSTGRES_RAM=$(( 3*${RAM_MB}/4  ))
export POSTGRES_MAX_CONNECTIONS=180
export POSTGRES_SHARED_BUFFERS=$(( ${POSTGRES_RAM}/4 ))MB
export POSTGRES_EFFECTIVE_CACHE_SIZE=$(( 3*${POSTGRES_RAM}/4 ))MB
export POSTGRES_MAINTENANCE_WORK_MEM=$(( ${POSTGRES_RAM}/16 ))MB
export CPU_WORKER_CORES=$(( (${CPU_CORES} - 6) / 2 ))
if (( ${CPU_WORKER_CORES} < 1 )); then
  export CPU_WORKER_CORES=1
fi
echo "${CPU_WORKER_CORES} worker CPU cores"

export POWA_NGINX_PORT=445
export POSTGRES_DISK=hdd

if [[ ${POSTGRES_DISK} = "ssd" ]]; then
    export POSTGRES_RANDOM_PAGE_COST=1.1
    export POSTGRES_EFFECTIVE_IO_CONCURRENCY=200
else
    export POSTGRES_RANDOM_PAGE_COST=4
    export POSTGRES_EFFECTIVE_IO_CONCURRENCY=2
fi

export POSTGRES_MIN_WAL_SIZE=4GB
export POSTGRES_MAX_WAL_SIZE=16GB

export POSTGRES_PARALLEL_WORKERS_PER_GATHER=$(( (${POSTGRES_CPUS}+2-1)/2 ))  # ceil (cpus / 2)

export POSTGRES_MAX_PARALLEL_MAINTENANCE_WORKERS=$(( (${POSTGRES_CPUS}+2-1)/2 ))  # ceil (cpus / 2)

if (( ${POSTGRES_MAX_PARALLEL_MAINTENANCE_WORKERS} > 4 )); then
    export POSTGRES_MAX_PARALLEL_MAINTENANCE_WORKERS=4
fi

# ((RAM - shared_buffers) / (max_connections * 3) / max_parallel_workers_per_gather / 2)
# /2 - is for data warehouses
# calculating with bc to avoid bad rounding on standard bash calculations
export POSTGRES_WORK_MEM=$(echo "scale=4;1024*0.75*${POSTGRES_RAM}/(${POSTGRES_MAX_CONNECTIONS}*3)/${POSTGRES_PARALLEL_WORKERS_PER_GATHER}"|bc)
# now rounding the end value
export POSTGRES_WORK_MEM=$(echo ${POSTGRES_WORK_MEM%%.*})kB


export CONTRAXSUITE_ROOT=../contraxsuite_services

export DOCKER_HOST_NAME_PG=contrax-db
export DOCKER_HOST_NAME_PG_ACCESS=tasks.contrax-db
export DOCKER_HOST_NAME_REDIS=contrax-redis
export DOCKER_HOST_NAME_REDIS_ACCESS=tasks.${DOCKER_HOST_NAME_REDIS}
export DOCKER_HOST_NAME_RABBITMQ=contrax-rabbitmq
export DOCKER_HOST_NAME_RABBITMQ_ACCESS=tasks.${DOCKER_HOST_NAME_RABBITMQ}
# Host name for Elastic should not contain underscores. Logstash crashes if seeing them in ES URL.
export DOCKER_HOST_NAME_ELASTICSEARCH=contrax-elasticsearch
export DOCKER_HOST_NAME_ELASTICSEARCH_ACCESS=tasks.${DOCKER_HOST_NAME_ELASTICSEARCH}
export DOCKER_HOST_NAME_UWSGI=contrax-uwsgi
export DOCKER_HOST_NAME_KIBANA=contrax-kibana
export DOCKER_HOST_NAME_DAPHNE=contrax-daphne
export DOCKER_HOST_NAME_DAPHNE_ACCESS=tasks.${DOCKER_HOST_NAME_DAPHNE}
export DOCKER_HOST_NAME_ELASTALERT_SERVER=contrax-elastalert
export DOCKER_HOST_NAME_TEXT_EXTRACTION_SYSTEM_API=tes-web-api
export DOCKER_TEXT_EXTRACTION_SYSTEM_API_PORT=8000
export DOCKER_TEXT_EXTRACTION_SYSTEM_URL=http://tasks.${DOCKER_HOST_NAME_TEXT_EXTRACTION_SYSTEM_API}:${DOCKER_TEXT_EXTRACTION_SYSTEM_API_PORT}

export DOCKER_ELASTALERT_SERVER_PORT=3030
export DOCKER_ELASTALERT_EMAIL_SSL=False


export DOCKER_ELASTICSEARCH_REPLICAS=1
export DOCKER_ELASTICSEARCH_PORT=9200


export DOCKER_PG_REPLICAS=1
export DOCKER_PG_USER=contrax1
export DOCKER_PG_PASSWORD=contrax1
export DOCKER_PG_DB_NAME=contrax1
export DOCKER_PG_MAX_BACKUP_NUMBER=3
export DOCKER_PG_PORT=5432

export DOCKER_PGBOUNCER_TRANS_HOST=contrax-pgbouncer-transaction
export DOCKER_PGBOUNCER_SESS_HOST=contrax-pgbouncer-session
export DOCKER_PGBOUNCER_PORT=5432


export DOCKER_PGBOUNCER_TRANS_MAX_CLIENT_CONN=1000
export DOCKER_PGBOUNCER_TRANS_SERVER_RESET_QUERY="DISCARD ALL"
export DOCKER_PGBOUNCER_TRANS_DEFAULT_POOL_SIZE=150

export DOCKER_PGBOUNCER_SESS_MAX_CLIENT_CONN=1000
export DOCKER_PGBOUNCER_SESS_SERVER_RESET_QUERY="DISCARD ALL"
export DOCKER_PGBOUNCER_SESS_DEFAULT_POOL_SIZE=20

export DJANGO_CELERY_DB_NAME=${DOCKER_PG_DB_NAME}
export DJANGO_CELERY_DB_USER=${DOCKER_PG_USER}
export DJANGO_CELERY_DB_PASSWORD=${DOCKER_PG_PASSWORD}
export DJANGO_CELERY_DB_HOST=
export DJANGO_CELERY_DB_PORT=
export DJANGO_CELERY_CONN_MAX_AGE=500

export DJANGO_WEBSRV_DB_NAME=${DOCKER_PG_DB_NAME}
export DJANGO_WEBSRV_DB_USER=${DOCKER_PG_USER}
export DJANGO_WEBSRV_DB_PASSWORD=${DOCKER_PG_PASSWORD}
export DJANGO_WEBSRV_DB_HOST=
export DJANGO_WEBSRV_DB_PORT=
export DJANGO_WEBSRV_CONN_MAX_AGE=0  # otherwise we have connection leakage in Daphne

export DOCKER_RABBITMQ_REPLICAS=1
export DOCKER_RABBITMQ_VHOST=contrax1_vhost
export DOCKER_RABBITMQ_USER=contrax1
export DOCKER_RABBITMQ_PASSWORD=contrax1

export DOCKER_JUPYTER_BASE_URL=/jupyter
export DOCKER_JUPYTER_HOST_NAME=contrax-jupyter
export DOCKER_JUPYTER_PORT=8888

export DOCKER_KIBANA_BASE_PATH=/kibana

export DOCKER_SLACK_WEBHOOK_URL=
export DOCKER_SLACK_CHANNEL=

export DOCKER_DJANGO_HOST_NAME=localhost
export DOCKER_DJANGO_EMAIL_BACKEND=smtp.CustomEmailBackend
export DOCKER_DJANGO_EMAIL_HOST=localhost
# Base path should start and end with slashes
export DOCKER_DJANGO_BASE_PATH=/explorer/
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
export DOCKER_WEBDAV_SERVER_NAME_ACCESS=tasks.${DOCKER_WEBDAV_SERVER_NAME}
export DOCKER_WEBDAV_AUTH_USER=user
export DOCKER_WEBDAV_AUTH_PASSWORD=password

export DOCKER_FLOWER_BASE_PATH=flower
export DOCKER_HOST_NAME_FLOWER=contrax-flower
export FLOWER_REPLICAS=0


export SHARED_USER_ID=65432
export SHARED_USER_NAME=contraxsuite_docker_user

export SHARED_USER_LOG_READER_ID=65431
export SHARED_USER_LOG_READER_NAME=contraxsuite_docker_log_reader


export DOCKER_REGISTRY=
export CONTRAXSUITE_IMAGE=lexpredict/lexpredict-contraxsuite:latest

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
export DOCKER_ELASTICSEARCH_CPUS=2
export DOCKER_ELASTICSEARCH_MEMORY=4G
export DOCKER_ELASTALERT_CPU=1
export DOCKER_ELASTALERT_MEMORY=2G
export DOCKER_TIKA_CPU=2
export DOCKER_TIKA_MEMORY=4G

export DISTR_DOCKER_IMAGE_URL=
export DISTR_DOCKER_IMAGE_NAME=
export DISTR_DEPLOY_SCRIPTS_URL=
export DISTR_USER=
export DISTR_PASSWORD=


export DOCKER_MINIO_BASE_URL=/minio
export DOCKER_MINIO_HOST_NAME=contrax-minio
export DOCKER_MINIO_PORT=9000

export DOCKER_MLFLOW_TRACKING_BASE_URL=/mlflow_tracking
export DOCKER_MLFLOW_TRACKING_HOST_NAME=contrax-mlflow-tracking
export DOCKER_MLFLOW_TRACKING_PORT=5000

export MLFLOW_S3_ENDPOINT_URL=http://contrax-minio:9000
export MLFLOW_AWS_BUCKET=contraxmlflowartifacts
export MLFLOW_AWS_ACCESS_KEY=${DOCKER_DJANGO_ADMIN_NAME}
export MLFLOW_AWS_SECRET_KEY=${DOCKER_DJANGO_ADMIN_PASSWORD}

export PG_STATISTICS_ENABLED=true

#export DOCKER_COMPOSE_FILE=docker-compose-single-master-many-workers.yml
export DOCKER_COMPOSE_FILE=docker-compose-single-host.yml

export DOCKER_SWARM_ADVERTISE_ADDR=

export LEXNLP_TIKA_PARSER_MODE=pdf_ocr

export UWSGI_PRIMARY_MIGRATIONS=

export DEBUG_TRACE_UPDATE_PARENT_TASK=False
export DEBUG_LOG_TASK_RUN_COUNT=False
export DEBUG_TRACK_LOCATING_PERFORMANCE=False
export DEBUG_SLOW_DOWN_FIELD_FORMULAS_SEC=0
export DEBUG_SLOW_DOWN_HIDE_UNTIL_FORMULAS_SEC=0

export PROXY_SERVER_HTTP=
export PROXY_SERVER_HTTPS=
export PROXY_NO_PROXY=localhost,127.0.0.1,contrax-webdav,contrax-minio,contrax-mlflow-tracking,contrax-redis,contrax-elasticsearch,contrax-daphne,tes-web-api,tasks.contrax-webdav,tasks.contrax-minio,tasks.contrax-mlflow-tracking,tasks.contrax-redis,tasks.contrax-elasticsearch,tasks.contrax-daphne,tasks.tes-web-api

# set to non-empty string to enable aioredis debug logging
export AIOREDIS_DEBUG=

export MODEL_S3_SSL_VERIFY=True

export DEPLOY_BACKEND_DEV=false

if [ -f setenv_local.sh ]
then
    echo "Loading setenv_local.sh"
    source setenv_local.sh
fi

export DOCKER_FRONTEND_ROOT_URL=${DOCKER_DJANGO_HOST_NAME}

export DOCKER_POSTGRES_LOG_MIN_DUR_STMT=-1
export DOCKER_DJANGO_BASE_PATH_STRIPPED=${DOCKER_DJANGO_BASE_PATH%/}

if [ -z "${DJANGO_WEBSRV_DB_HOST}" ]; then
    export DJANGO_WEBSRV_DB_HOST=tasks.${DOCKER_PGBOUNCER_SESS_HOST}
    export DJANGO_WEBSRV_DB_PORT=${DOCKER_PGBOUNCER_PORT}
    export DJANGO_WEBSRV_DB_NAME=${DOCKER_PG_DB_NAME}
    export DJANGO_WEBSRV_DB_USER=${DOCKER_PG_USER}
    export DJANGO_WEBSRV_DB_PASSWORD=${DOCKER_PG_PASSWORD}
fi

if [ -z "${DJANGO_CELERY_DB_HOST}" ]; then
    export DJANGO_CELERY_DB_HOST=tasks.${DOCKER_PGBOUNCER_TRANS_HOST}
    export DJANGO_CELERY_DB_PORT=${DOCKER_PGBOUNCER_PORT}
    export DJANGO_CELERY_DB_NAME=${DOCKER_PG_DB_NAME}
    export DJANGO_CELERY_DB_USER=${DOCKER_PG_USER}
    export DJANGO_CELERY_DB_PASSWORD=${DOCKER_PG_PASSWORD}
fi