#!/bin/bash
set -e

pushd ../

source setenv.sh
if [ -e setenv_local.sh ]
then
    source setenv_local.sh
fi

VOLUME=/var/lib/docker/volumes/deploy_contraxsuite_third_party_dependencies/_data/
sudo mkdir -p ${VOLUME}
sudo cp ${DOCKER_DJANGO_THEME_ARCHIVE} ${VOLUME}
sudo cp ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} ${VOLUME}
sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME}

if [ ! -z ${DOCKER_NGINX_CERTIFICATE} ]; then
    VOLUME=/var/lib/docker/volumes/docker_contraxsuite_nginx_certs/_data/
    sudo mkdir -p ${VOLUME}
    sudo cp ${DOCKER_NGINX_CERTIFICATE} ${VOLUME}/certificate.pem
    sudo cp ${DOCKER_NGINX_CERTIFICATE_KEY} ${VOLUME}/certificate.key
    sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME}
fi
popd

sudo -E docker-compose up --scale contrax_celery=1
# docker-compose run contrax_uwsgi /start.sh uwsgi shell
# docker-compose run contrax_uwsgi /bin/sh