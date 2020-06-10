#!/bin/bash
set -e

pushd ../

export DOLLAR='$' # escape $ in envsubst
export DOCKER_COMPOSE_CONFIG_VERSION=`date +%Y%m%d%H%M%S`

# We use bc for numeric calculations in setenv.sh
sudo apt-get install -y bc

source setenv.sh
if [ -e setenv_local.sh ]
then
    source setenv_local.sh
fi
source volumes.sh

source util/fix_nginx_logs.sh
source util/configure_host.sh

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
   export DOCKER_FRONTEND_ROOT_URL=${DOCKER_DJANGO_HOST_NAME}
fi

if sudo [ -f ${VOLUME_NGINX_CERTS}/certificate.pem ]; then
    echo "Nginx will serve HTTPS."
    envsubst < ./config-templates/nginx-https.conf.template > ./temp/default.conf
else
    echo "Nginx will serve plain HTTP."
    envsubst < ./config-templates/nginx-http.conf.template > ./temp/default.conf
fi

envsubst < ./config-templates/postgresql.template.conf > ./temp/postgresql.conf
if [ "${PG_STATISTICS_ENABLED}" = true ]; then
    if [ "${POWA_ENABLED,,}" = "true" ]; then
        echo "POWA is enabled. Adding to Postgres."
    	echo "shared_preload_libraries = 'pg_stat_statements,powa,pg_stat_kcache,pg_qualstats'" >> ./temp/postgresql.conf
	    export POWA_WEB_REPLICAS=1
        export POWA_INSTALL="apt-get update && apt-get install -y --no-install-recommends postgresql-11-powa postgresql-11-pg-qualstats postgresql-11-pg-stat-kcache postgresql-11-hypopg && rm -rf /var/lib/apt/lists/* &&"
        envsubst < ./config-templates/nginx-powa.conf.template > ./temp/powa.conf
        sudo cp ./temp/powa.conf ${VOLUME_NGINX_CONF}/conf.d/powa.conf
    else
        echo "POWA is disabled."
	    echo "shared_preload_libraries = 'pg_stat_statements'" >> ./temp/postgresql.conf
	    export POWA_WEB_REPLICAS=0
    fi
    echo "pg_stat_statements.max = 1000" >> ./temp/postgresql.conf
    echo "pg_stat_statements.track = all" >> ./temp/postgresql.conf
else
    export POWA_WEB_REPLICAS=0
fi

sudo cp ./temp/nginx.conf ${VOLUME_NGINX_CONF}/nginx.conf
sudo cp ./temp/internal.conf ${VOLUME_NGINX_CONF}/conf.d/internal.conf
sudo cp ./temp/default.conf ${VOLUME_NGINX_CONF}/conf.d/default.conf

envsubst < ./config-templates/metricbeat.yml.template > ./temp/metricbeat.yml
envsubst < ./config-templates/filebeat.template.yml > ./temp/filebeat.yml
envsubst < ./config-templates/elasticsearch.yml.template > ./temp/elasticsearch.yml
envsubst < ./config-templates/elastalert-config.yaml.template > ./temp/elastalert-config.yaml
envsubst < ./config-templates/elastalert-smtp-auth.yaml > ./temp/elastalert-smtp-auth.yaml
envsubst < ./config-templates/elastalert-server-config.json.template > ./temp/elastalert-server-config.json
envsubst < ./config-templates/kibana.yml.template > ./temp/kibana.yml
envsubst < ./config-templates/db-backup.sh.template > ./temp/db-backup.sh
envsubst < ./config-templates/postgres_init.sql.template > ./temp/postgres_init.sql
envsubst < ./config-templates/powa-web.conf.template > ./temp/powa-web.conf

envsubst < ./config-templates/local_settings_celery.py.template > ./temp/local_settings_celery.py
envsubst < ./config-templates/local_settings_websrv.py.template > ./temp/local_settings_websrv.py
envsubst < ./config-templates/uwsgi.ini.template > ./temp/uwsgi.ini

envsubst < ./config-templates/elastalert-examples/elastalert-disk-usage.yaml > ./temp/elastalert-disk-usage.yaml
envsubst < ./config-templates/elastalert-examples/elastalert-task-failed.yaml > ./temp/elastalert-task-failed.yaml
envsubst < ./config-templates/elastalert-examples/elastalert-down-docker-services.yaml > ./temp/elastalert-down-docker-services.yaml
envsubst < ./config-templates/elastalert-examples/elastalert-bad-gateway-error.yaml > ./temp/elastalert-bad-gateway-error.yaml

envsubst < ./config-templates/jupyter_notebook_config.py.template > ./temp/jupyter_notebook_config.py

if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-disk-usage.yaml ]; then
    sudo cp ./temp/elastalert-disk-usage.yaml ${VOLUME_ELASTALERT_RULES}/
fi
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-task-failed.yaml ]; then
    sudo cp ./temp/elastalert-task-failed.yaml ${VOLUME_ELASTALERT_RULES}/
fi
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-down-docker-services.yaml ]; then
    sudo cp ./temp/elastalert-down-docker-services.yaml ${VOLUME_ELASTALERT_RULES}/
fi
if [ ! -f ${VOLUME_ELASTALERT_RULES}/elastalert-bad-gateway-error.yaml ]; then
    sudo cp ./temp/elastalert-bad-gateway-error.yaml ${VOLUME_ELASTALERT_RULES}/
fi

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
export UWSGI_INI_CONFIG_VERSION=`md5sum ./temp/uwsgi.ini | awk '{ print $1 }'`
export JUPYTER_CONFIG_VERSION=`md5sum ./temp/jupyter_notebook_config.py | awk '{ print $1 }'`

envsubst < ./docker-compose-templates/${DOCKER_COMPOSE_FILE} > ./temp/${DOCKER_COMPOSE_FILE}

echo "Updating hosts file"
export DOCKER_NODE_IP=$(sudo docker run -it --net=host codenvy/che-ip | tr -d '\r')
sudo sed -i "/$DOCKER_DJANGO_HOST_NAME/d" /etc/hosts
grep -qxF "$DOCKER_NODE_IP $DOCKER_DJANGO_HOST_NAME" /etc/hosts || sudo bash -c "echo $DOCKER_NODE_IP $DOCKER_DJANGO_HOST_NAME >> /etc/hosts"

echo "Updating notification webhooks url"

sudo crontab -l > crontemp && cat crontemp | sed -r "s|[^ ]*https:\/\/hooks\.slack\.com\/[^ ]*|$SLACK_WEBHOOK_URL|g" > hooktemp && cat hooktemp | sudo crontab - && rm crontemp && rm hooktemp

echo "Refreshing scheduled Cron tasks"

sudo crontab -l > crontemp && cat crontemp | grep "sudo docker system prune -af" >/dev/null || echo "0 0 * * * sudo docker system prune -af > /dev/null 2>&1" >> crontemp && cat crontemp | sudo crontab - && rm crontemp
sudo crontab -l > crontemp && cat crontemp | grep "sudo bash es_recovery.sh" >/dev/null || echo "0,15,30,45 * * * * cd /data/deploy/contraxsuite-deploy/docker/util && sudo bash es_recovery.sh ${SLACK_WEBHOOK_URL} > /dev/null 2>&1" >> crontemp && cat crontemp | sudo crontab - && rm crontemp
sudo crontab -l > crontemp && cat crontemp | grep "sudo bash remove_down_nodes.sh" >/dev/null || echo "1,11,21,31,41,51 * * * * cd /data/deploy/contraxsuite-deploy/docker/util && sudo bash remove_down_nodes.sh > /dev/null 2>&1" >> crontemp && cat crontemp | sudo crontab - && rm crontemp
sudo crontab -l > crontemp && cat crontemp | grep "sudo bash monitor_docker_services.sh" >/dev/null || echo "0,15,30,45 * * * * cd /data/deploy/contraxsuite-deploy/docker/util && sudo bash monitor_docker_services.sh > /dev/null 2>&1" >> crontemp && cat crontemp | sudo crontab - && rm crontemp
sudo crontab -l > crontemp && cat crontemp | grep "sudo bash monitor_disk_usage.sh" >/dev/null || echo "* * * * * cd /data/deploy/contraxsuite-deploy/docker/util && sudo bash monitor_disk_usage.sh > /dev/null 2>&1" >> crontemp && cat crontemp | sudo crontab - && rm crontemp
sudo crontab -l > crontemp && cat crontemp | grep "sudo bash collect_docker_stats.sh" >/dev/null || echo "* * * * * cd /data/deploy/contraxsuite-deploy/docker/util && sudo bash collect_docker_stats.sh > /dev/null 2>&1" >> crontemp && cat crontemp | sudo crontab - && rm crontemp

echo "Starting with image: ${CONTRAXSUITE_IMAGE_FULL_NAME}:${CONTRAXSUITE_IMAGE_VERSION}"

echo "Starting with docker-compose config: ${DOCKER_COMPOSE_FILE}"

sudo -E docker stack deploy --with-registry-auth --compose-file ./temp/${DOCKER_COMPOSE_FILE} contraxsuite

echo "Restarting Nginx if container exists"
for i in {1..30}
do
  NGINX_CONTAINER_ID="$(sudo docker ps --filter "name=contraxsuite_contrax-nginx" --format "{{.ID}}")"
  if [ ${NGINX_CONTAINER_ID} ]; then
    sudo docker exec "${NGINX_CONTAINER_ID}" sh -c "nginx -s reload" && break
  fi
  if [ $i == 30 ]; then
    echo "Failed to reload Nginx"; exit 1
  fi
  sleep 6s
done

echo "Deploy routines have been completed"
