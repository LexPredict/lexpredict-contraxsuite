#!/bin/bash

# to be executed as root in docker/deploy dir

set -e

# We use bc for numeric calculations in setenv.sh
apt-get install -y bc

pushd ../  # /docker

source setenv.sh
source volumes.sh

source util/fix_nginx_logs.sh
source util/configure_host.sh


if [[ -f "${DOCKER_DJANGO_JQWIDGETS_ARCHIVE}" ]]; then
    echo "Copying jqwidgets archive from ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} to the volume..."
    cp ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE} ${VOLUME_THIRD_PARTY}
    chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_THIRD_PARTY}
fi

popd  # /docker/deploy

if [[ "${DEPLOY_BACKEND_DEV}" = "true" ]]; then
  pushd ../../ > /dev/null
  export PROJECT_ROOT=$(pwd)
  popd > /dev/null
fi

source prepare_configs.sh


# Calculating md5 sums of the config files to use as their versions.
# This is done for docker swarm to see the updated configs if their contents changed.
export NGINX_CUSTOMER_CONF_VERSION=`md5sum ./temp/nginx-customer.conf | awk '{ print $1 }'`
export METRICBEAT_CONFIG_VERSION=`md5sum ./temp/metricbeat.yml | awk '{ print $1 }'`
export ELASTICSEARCH_CONFIG_VERSION=`md5sum ./temp/elasticsearch.yml | awk '{ print $1 }'`
export KIBANA_CONFIG_VERSION=`md5sum ./temp/kibana.yml | awk '{ print $1 }'`
export ELASTALERT_CONFIG_VERSION=`md5sum ./temp/elastalert-config.yaml | awk '{ print $1 }'`
export ELASTALERT_SERVER_CONFIG_VERSION=`md5sum ./temp/elastalert-server-config.json | awk '{ print $1 }'`
export ELASTALERT_SMTP_AUTH_VERSION=`md5sum ./temp/elastalert-smtp-auth.yaml | awk '{ print $1 }'`
export LOGROTATE_CONFIG_VERSION=`md5sum ./temp/logrotate.conf | awk '{ print $1 }'`
export LOGS_CRON_CONFIG_VERSION=`md5sum ./temp/logs-cron.conf | awk '{ print $1 }'`
export PG_CONFIG_VERSION=`md5sum ./temp/postgresql.conf | awk '{ print $1 }'`
export PG_BACKUP_SCRIPT_CONFIG_VERSION=`md5sum ./temp/db-backup.sh | awk '{ print $1 }'`
export PG_BACKUP_CRON_CONFIG_VERSION=`md5sum ./temp/backup-cron.conf | awk '{ print $1 }'`
export PG_INIT_SQL_CONFIG_VERSION=`md5sum ./temp/postgres_init.sql | awk '{ print $1 }'`
export POWA_WEB_CONFIG_VERSION=`md5sum ./temp/powa-web.conf | awk '{ print $1 }'`
export LOCAL_SET_WEBSRV_CONFIG_VERSION=`md5sum ./temp/local_settings_websrv.py | awk '{ print $1 }'`
export LOCAL_SET_CELERY_CONFIG_VERSION=`md5sum ./temp/local_settings_celery.py | awk '{ print $1 }'`
export PGBOUNCER_WEBSRV_CONFIG_VERSION=`md5sum ./temp/pgbouncer.websrv.ini | awk '{ print $1 }'`
export PGBOUNCER_CELERY_CONFIG_VERSION=`md5sum ./temp/pgbouncer.celery.ini | awk '{ print $1 }'`
export PGBOUNCER_USERLIST_VERSION=`md5sum ./temp/pgbouncer.userlist.txt | awk '{ print $1 }'`
export UWSGI_INI_CONFIG_VERSION=`md5sum ./temp/uwsgi.ini | awk '{ print $1 }'`
export JUPYTER_CONFIG_VERSION=`md5sum ./temp/jupyter_notebook_config.py | awk '{ print $1 }'`
export RABBITMQ_CONFIG_VERSION=`md5sum ./temp/rabbitmq.conf | awk '{ print $1 }'`


if [[ "${DEPLOY_BACKEND_DEV}" = "true" ]]; then
  # For local development we use the special compose file
  export DOCKER_COMPOSE_FILE="docker-compose-backend-develop.yml"

  # Overwrite the filebeat config with the one which
  # fetches logs from the local dir
  mv -f ./temp/filebeat-backend-dev.yml ./temp/filebeat.yml
fi

export FILEBEAT_CONFIG_VERSION=`md5sum ./temp/filebeat.yml | awk '{ print $1 }'`

envsubst < ./docker-compose-templates/${DOCKER_COMPOSE_FILE} > ./temp/${DOCKER_COMPOSE_FILE}

echo "Copying Nginx error pages to its volume..."
cp -a ./nginx-error-pages/. ${VOLUME_NGINX_ERROR_PAGES}

echo "Copying Nginx configs to its volume..."
cp -a ./config-templates/nginx/. ${VOLUME_NGINX_CONF}
cp ./temp/nginx.conf ${VOLUME_NGINX_CONF}/nginx.conf
cp ./temp/internal.conf ${VOLUME_NGINX_CONF}/conf.d/internal.conf
cp ./temp/default.conf ${VOLUME_NGINX_CONF}/conf.d/default.conf

echo "Updating frontend file permissions..."
chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_FRONTEND}

if [ ! -f ${VOLUME_NGINX_CONF}/.kibana_htpasswd ]; then
    echo "Setting default password for HTTP basic auth for Kibana, Jupyter and other services..."
    apt-get install -y apache2-utils
    htpasswd -b -c ${VOLUME_NGINX_CONF}/.kibana_htpasswd ${DOCKER_DJANGO_ADMIN_NAME} ${DOCKER_DJANGO_ADMIN_PASSWORD}
fi

if [ ! -z ${DOCKER_NGINX_CERTIFICATE} ]; then
    echo "Pre-defined certificates for NGINX provided."
    echo "Certificate: ${DOCKER_NGINX_CERTIFICATE}"
    echo "Certificate key: ${DOCKER_NGINX_CERTIFICATE_KEY}"
    echo "Copying Nginx HTTPS certificate and key to its volume..."
    cp ${DOCKER_NGINX_CERTIFICATE} ${VOLUME_NGINX_CERTS}/certificate.pem
    cp ${DOCKER_NGINX_CERTIFICATE_KEY} ${VOLUME_NGINX_CERTS}/certificate.key
    chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} ${VOLUME_NGINX_CERTS}
fi

echo "Copying default Elastalert configuration..."
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-disk-usage.yaml ]; then
    cp ./temp/elastalert-disk-usage.yaml ${VOLUME_ELASTALERT_RULES}/
fi
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-task-failed.yaml ]; then
    cp ./temp/elastalert-task-failed.yaml ${VOLUME_ELASTALERT_RULES}/
fi
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-down-docker-services.yaml ]; then
    cp ./temp/elastalert-down-docker-services.yaml ${VOLUME_ELASTALERT_RULES}/
fi
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-bad-gateway-error.yaml ]; then
    cp ./temp/elastalert-bad-gateway-error.yaml ${VOLUME_ELASTALERT_RULES}/
fi

echo "Updating hosts file"
export DOCKER_NODE_IP=$(docker run -it --net=host codenvy/che-ip | tr -d '\r')
sed -i "/$DOCKER_DJANGO_HOST_NAME/d" /etc/hosts
grep -qxF "$DOCKER_NODE_IP $DOCKER_DJANGO_HOST_NAME" /etc/hosts || bash -c "echo $DOCKER_NODE_IP $DOCKER_DJANGO_HOST_NAME >> /etc/hosts"

echo "Updating notification webhooks url"

crontab -l > crontemp && cat crontemp | sed -r "s|[^ ]*https:\/\/hooks\.slack\.com\/[^ ]*|$SLACK_WEBHOOK_URL|g" > hooktemp && cat hooktemp | crontab - && rm crontemp && rm hooktemp

echo "Refreshing scheduled Cron tasks"

crontab -l > crontemp && cat crontemp | grep "docker system prune -af" >/dev/null || echo "0 0 * * * docker system prune -af > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp
crontab -l > crontemp && cat crontemp | grep "bash es_recovery.sh" >/dev/null || echo "0,15,30,45 * * * * cd /data/deploy/contraxsuite-deploy/docker/util && bash es_recovery.sh ${SLACK_WEBHOOK_URL} > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp
crontab -l > crontemp && cat crontemp | grep "bash remove_down_nodes.sh" >/dev/null || echo "1,11,21,31,41,51 * * * * cd /data/deploy/contraxsuite-deploy/docker/util && bash remove_down_nodes.sh > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp
crontab -l > crontemp && cat crontemp | grep "bash monitor_docker_services.sh" >/dev/null || echo "0,15,30,45 * * * * cd /data/deploy/contraxsuite-deploy/docker/util && bash monitor_docker_services.sh > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp
crontab -l > crontemp && cat crontemp | grep "bash monitor_disk_usage.sh" >/dev/null || echo "* * * * * cd /data/deploy/contraxsuite-deploy/docker/util && bash monitor_disk_usage.sh > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp
crontab -l > crontemp && cat crontemp | grep "bash collect_docker_stats.sh" >/dev/null || echo "* * * * * cd /data/deploy/contraxsuite-deploy/docker/util && bash collect_docker_stats.sh > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp

echo "Starting with image: ${CONTRAXSUITE_IMAGE}"

echo "Starting with docker-compose config: ${DOCKER_COMPOSE_FILE}"

docker stack deploy --compose-file ./temp/${DOCKER_COMPOSE_FILE} contraxsuite --with-registry-auth

echo "Checking RabbitMQ queues"
source ../util/check_rabbit_queues.sh || true

echo "Restarting Nginx if container exists"
for i in {1..30}
do
  NGINX_CONTAINER_ID="$(docker ps --filter "name=contraxsuite_contrax-nginx" --format "{{.ID}}")"
  if [ ${NGINX_CONTAINER_ID} ]; then
    docker exec "${NGINX_CONTAINER_ID}" sh -c "nginx -s reload" && break
  fi
  if [ $i == 30 ]; then
    echo "Failed to reload Nginx"; exit 1
  fi
  sleep 6s
done

echo "Deploy routines have been completed"
