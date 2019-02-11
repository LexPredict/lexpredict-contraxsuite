#!/bin/bash
set -e

pushd ../

export DOLLAR='$' # escape $ in envsubst
export DOCKER_COMPOSE_CONFIG_VERSION=`date +%Y%m%d%H%M%S`

source setenv.sh
if [ -e setenv_local.sh ]
then
    source setenv_local.sh
fi
source volumes.sh

source util/configure_host.sh

sudo cp ${DOCKER_DJANGO_THEME_ARCHIVE} ${VOLUME_THIRD_PARTY}
sudo cp ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} ${VOLUME_THIRD_PARTY}
sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_THIRD_PARTY}

popd

mkdir -p ./temp

sudo cp -a ./config-templates/nginx/. ${VOLUME_NGINX_CONF}
envsubst < ./config-templates/nginx.conf.template > ./temp/nginx.conf
envsubst < ./config-templates/nginx-internal.conf.template > ./temp/internal.conf

if sudo [ ! -f ${VOLUME_NGINX_CONF}/.kibana_htpasswd ]; then
    sudo apt-get install -y apache2-utils
    sudo htpasswd -b -c ${VOLUME_NGINX_CONF}/.kibana_htpasswd ${DOCKER_DJANGO_ADMIN_NAME} ${DOCKER_DJANGO_ADMIN_PASSWORD}
fi

if sudo [ ! -z ${DOCKER_NGINX_CERTIFICATE} ]; then
    sudo cp ${DOCKER_NGINX_CERTIFICATE} ${VOLUME_NGINX_CERTS}/certificate.pem
    sudo cp ${DOCKER_NGINX_CERTIFICATE_KEY} ${VOLUME_NGINX_CERTS}/certificate.key
    sudo chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_NGINX_CERTS}
fi

export NGINX_EXTERNAL_ROUTES=$(envsubst < ./config-templates/nginx-external-routes.conf.template | sed 's/^/    /')
if sudo [ ! -z "$(sudo ls -A ${VOLUME_FRONTEND})" ]; then
   NGINX_FORNTEND_ROUTES=$(envsubst < ./config-templates/nginx-frontend-routes.conf.template | sed 's/^/    /')
   export NGINX_EXTERNAL_ROUTES=${NGINX_FORNTEND_ROUTES}$'\n\n'${NGINX_EXTERNAL_ROUTES}
fi

if sudo [ -f ${VOLUME_NGINX_CERTS}/certificate.pem ]; then
    echo "Nginx will serve HTTPS."
    envsubst < ./config-templates/nginx-https.conf.template > ./temp/default.conf
else
    echo "Nginx will serve plain HTTP."
    envsubst < ./config-templates/nginx-http.conf.template > ./temp/default.conf
fi

envsubst < ./config-templates/postgresql.conf.template > ./temp/postgresql.conf
if [ ${PG_STATISTICS_ENABLED} = true ]; then
    echo "shared_preload_libraries = 'pg_stat_statements'" >> ./temp/postgresql.conf
    echo "pg_stat_statements.max = 1000" >> ./temp/postgresql.conf
    echo "pg_stat_statements.track = all" >> ./temp/postgresql.conf
fi

sudo cp ./temp/nginx.conf ${VOLUME_NGINX_CONF}/nginx.conf
sudo cp ./temp/internal.conf ${VOLUME_NGINX_CONF}/conf.d/internal.conf
sudo cp ./temp/default.conf ${VOLUME_NGINX_CONF}/conf.d/default.conf

envsubst < ./config-templates/metricbeat.yml.template > ./temp/metricbeat.yml
envsubst < ./config-templates/filebeat.yml.template > ./temp/filebeat.yml
envsubst < ./config-templates/elasticsearch.yml.template > ./temp/elasticsearch.yml
envsubst < ./config-templates/db-backup.sh.template > ./temp/db-backup.sh
envsubst < ./config-templates/postgres_init.sql.template > ./temp/postgres_init.sql

NGINX_CUSTOMER_TEMPLATE=./config-templates/nginx-customer.conf.template
NGINX_CUSTOMER_CONF=./temp/nginx-customer.conf

if [ -f ${NGINX_CUSTOMER_TEMPLATE} ]; then
    envsubst < ${NGINX_CUSTOMER_TEMPLATE} > ${NGINX_CUSTOMER_CONF}
else
    echo '# no customer config included' > ${NGINX_CUSTOMER_CONF}
fi
export NGINX_CUSTOMER_CONF_VERSION=`md5sum ${NGINX_CUSTOMER_CONF} | awk '{ print $1 }'`

cp ./config-templates/*.conf ./temp/

export FILEBEAT_CONFIG_VERSION=`md5sum ./temp/filebeat.yml | awk '{ print $1 }'`
export METRICBEAT_CONFIG_VERSION=`md5sum ./temp/metricbeat.yml | awk '{ print $1 }'`
export ELASTICSEARCH_CONFIG_VERSION=`md5sum ./temp/elasticsearch.yml | awk '{ print $1 }'`
export LOGROTATE_CONFIG_VERSION=`md5sum ./temp/logrotate.conf | awk '{ print $1 }'`
export LOGS_CRON_CONFIG_VERSION=`md5sum ./temp/logs-cron.conf | awk '{ print $1 }'`
export PG_CONFIG_VERSION=`md5sum ./temp/postgresql.conf | awk '{ print $1 }'`
export PG_BACKUP_SCRIPT_CONFIG_VERSION=`md5sum ./temp/db-backup.sh | awk '{ print $1 }'`
export PG_BACKUP_CRON_CONFIG_VERSION=`md5sum ./temp/backup-cron.conf | awk '{ print $1 }'`
export PG_INIT_SQL_CONFIG_VERSION=`md5sum ./temp/postgres_init.sql | awk '{ print $1 }'`

envsubst < ./docker-compose-templates/${DOCKER_COMPOSE_FILE} > ./temp/${DOCKER_COMPOSE_FILE}


echo "Starting with image: ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION}"

echo "Starting with docker-compose config: ${DOCKER_COMPOSE_FILE}"

sudo -E docker stack deploy --compose-file ./temp/${DOCKER_COMPOSE_FILE} contraxsuite
