#!/bin/bash
set -e

pushd ../

source setenv.sh
if [ -e setenv_local.sh ]
then
    source setenv_local.sh
fi

VOLUME_THIRD_PARTY=${DOCKER_VOLUME_DIR}/contraxsuite_contraxsuite_third_party_dependencies/_data/
sudo mkdir -p ${VOLUME_THIRD_PARTY}
sudo cp ${DOCKER_DJANGO_THEME_ARCHIVE} ${VOLUME_THIRD_PARTY}
sudo cp ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} ${VOLUME_THIRD_PARTY}
sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_THIRD_PARTY}

if [ ! -z ${DOCKER_NGINX_CERTIFICATE} ]; then
    VOLUME_CERTS=/var/lib/docker/volumes/contraxsuite_contraxsuite_nginx_certs/_data/
    sudo mkdir -p ${VOLUME_CERTS}
    sudo cp ${DOCKER_NGINX_CERTIFICATE} ${VOLUME_CERTS}/certificate.pem
    sudo cp ${DOCKER_NGINX_CERTIFICATE_KEY} ${VOLUME_CERTS}/certificate.key
    sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_CERTS}
fi





popd

mkdir -p ./temp
envsubst < ./metricbeat.yml.template > ./temp/metricbeat.yml
envsubst < ./filebeat.yml.template > ./temp/filebeat.yml
envsubst < ./elasticsearch.yml.template > ./temp/elasticsearch.yml


sudo -E docker stack deploy --compose-file docker-compose.yml contraxsuite
#docker-compose run contrax_rabbitmq
