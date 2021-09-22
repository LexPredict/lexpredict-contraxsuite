#!/usr/bin/env bash

source setenv.sh
if [ -e ../setenv_local.sh ]
then
    source setenv_local.sh
fi

DOCKER_VOLUME_DIR=${DOCKER_DIR}/volumes

export VOLUME_NGINX_CONF=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_nginx_conf/_data/
export VOLUME_NGINX_ERROR_PAGES=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_nginx_error_pages/_data/
export VOLUME_NGINX_CERTS=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_nginx_certs/_data/
export VOLUME_LOGS=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_logs/_data
export VOLUME_INTERNAL_NGINX_LOGS=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_internal_nginx_logs/_data
export VOLUME_FRONTEND=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_frontend/_data/
export VOLUME_THIRD_PARTY=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_third_party_dependencies/_data/
export VOLUME_DB=${DOCKER_VOLUME_DIR}/contraxsuite_postgres_data_11/_data/
export VOLUME_REGISTRY=${DOCKER_VOLUME_DIR}/contraxsuite_registry_registry_storage/_data
export VOLUME_RABBIT=${DOCKER_VOLUME_DIR}/contraxsuite_rabbitmq_data/_data
export VOLUME_CELERY_WORK_STATE=${DOCKER_VOLUME_DIR}/contraxsuite_celery_worker_state/_data
export VOLUME_DATA_MEDIA=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_data_media/_data
export VOLUME_DATA_UPDATE=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_data_update/_data
export VOLUME_SSL_CERTS=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_ssl_certs/_data
export VOLUME_ELASTALERT_RULES=${DOCKER_VOLUME_DIR}/contraxsuite_elastalert_rules/_data


# Initialize volumes
sudo mkdir -p ${VOLUME_NGINX_CONF}
sudo mkdir -p ${VOLUME_NGINX_ERROR_PAGES}
sudo mkdir -p ${VOLUME_NGINX_CERTS}
sudo mkdir -p ${VOLUME_NGINX_CONF}/conf.d
sudo mkdir -p ${VOLUME_FRONTEND}
sudo mkdir -p ${VOLUME_THIRD_PARTY}
sudo mkdir -p ${VOLUME_DB}
sudo mkdir -p ${VOLUME_REGISTRY}
sudo mkdir -p ${VOLUME_DATA_UPDATE}
sudo mkdir -p ${VOLUME_SSL_CERTS}
sudo mkdir -p ${VOLUME_ELASTALERT_RULES}
