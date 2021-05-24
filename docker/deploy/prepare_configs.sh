#!/bin/bash

if [[ "${DOLLAR}" != '$' ]]; then
    echo "Looks like setenv.sh hasn't been sourced before running this script."
    exit 1
fi

# Filling config templates and putting the configs into temp dir
mkdir -p ./temp  # /docker/deploy/temp

# Postgres config
envsubst < ./config-templates/postgresql.template.conf > ./temp/postgresql.conf
if [ "${PG_STATISTICS_ENABLED}" = true ]; then
    if [ "${POWA_ENABLED,,}" = "true" ]; then
        echo "POWA is enabled. Adding to Postgres."
    	echo "shared_preload_libraries = 'pg_stat_statements,powa,pg_stat_kcache,pg_qualstats'" >> ./temp/postgresql.conf
	    export POWA_WEB_REPLICAS=1
        export POWA_INSTALL="apt-get update && apt-get install -y --no-install-recommends postgresql-11-powa postgresql-11-pg-qualstats postgresql-11-pg-stat-kcache postgresql-11-hypopg && rm -rf /var/lib/apt/lists/* &&"
        envsubst < ./config-templates/nginx-powa.conf.template > ./temp/powa.conf
        cp ./temp/powa.conf ${VOLUME_NGINX_CONF}/conf.d/powa.conf
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


# Nginx config
envsubst < ./config-templates/nginx.conf.template > ./temp/nginx.conf
envsubst < ./config-templates/nginx-internal.conf.template > ./temp/internal.conf

export NGINX_EXTERNAL_ROUTES=$(envsubst < ./config-templates/nginx-external-routes.conf.template | sed 's/^/    /')
if [ "${WITH_JS_FRONTEND,,}" = "true" ]; then
   NGINX_FORNTEND_ROUTES=$(envsubst < ./config-templates/nginx-frontend-routes.conf.template | sed 's/^/    /')
   export NGINX_EXTERNAL_ROUTES=${NGINX_FORNTEND_ROUTES}$'\n\n'${NGINX_EXTERNAL_ROUTES}
   export DOCKER_FRONTEND_ROOT_URL=${DOCKER_DJANGO_HOST_NAME}
fi

if [ "${WITH_HTTPS,,}" = "true" ]; then
    echo "Nginx will serve HTTPS."
    envsubst < ./config-templates/nginx-https.conf.template > ./temp/default.conf
else
    echo "Nginx will serve plain HTTP."
    envsubst < ./config-templates/nginx-http.conf.template > ./temp/default.conf
fi


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
envsubst < ./config-templates/pgbouncer.celery.template.ini > ./temp/pgbouncer.celery.ini
envsubst < ./config-templates/local_settings_websrv.py.template > ./temp/local_settings_websrv.py
envsubst < ./config-templates/pgbouncer.websrv.template.ini > ./temp/pgbouncer.websrv.ini
envsubst < ./config-templates/uwsgi.ini.template > ./temp/uwsgi.ini
envsubst < ./config-templates/pgbouncer.userlist.template.txt > ./temp/pgbouncer.userlist.txt

envsubst < ./config-templates/elastalert-examples/elastalert-disk-usage.yaml > ./temp/elastalert-disk-usage.yaml
envsubst < ./config-templates/elastalert-examples/elastalert-task-failed.yaml > ./temp/elastalert-task-failed.yaml
envsubst < ./config-templates/elastalert-examples/elastalert-down-docker-services.yaml > ./temp/elastalert-down-docker-services.yaml
envsubst < ./config-templates/elastalert-examples/elastalert-bad-gateway-error.yaml > ./temp/elastalert-bad-gateway-error.yaml

envsubst < ./config-templates/jupyter_notebook_config.py.template > ./temp/jupyter_notebook_config.py

envsubst < ./config-templates/nginx-customer.conf.template > ./temp/nginx-customer.conf || echo '# no customer config included' > ./temp/nginx-customer.conf

envsubst < ./config-templates/filebeat-backend-dev.template.yml > ./temp/filebeat-backend-dev.yml

cp ./config-templates/*.conf ./temp/

echo "Copy config to helm chart"
mkdir -p ./k8s/contraxsuite/files/
cp -r ./temp/* ./k8s/contraxsuite/files/

