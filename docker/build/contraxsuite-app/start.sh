#!/bin/bash

set -e

PROJECT_DIR="/contraxsuite_services"
VENV_PATH="/contraxsuite_services/venv/bin/activate"
ACTIVATE_VENV="export LANG=C.UTF-8 && cd ${PROJECT_DIR} && . ${VENV_PATH} "

echo ""
echo ===================================================================
echo "Build info:"
cat /build.info
echo "Build UUID:"
cat /build.uuid
echo "Going to start: $1..."
echo ===================================================================
echo ""


echo "Contraxsuite user name: ${SHARED_USER_NAME}"
echo "Contraxsuite user id: $(id -u ${SHARED_USER_NAME})"

pushd /contraxsuite_services

if [[ -z "${STARTUP_DEPS_READY_CMD}" ]]; then
    echo "No dependencies specified to wait. Starting up..."
else
    echo "Dependencies readiness test command: ${STARTUP_DEPS_READY_CMD}"
    while ! eval ${STARTUP_DEPS_READY_CMD}
    do
      echo "Dependencies are not ready. Waiting 5 seconds..."
      sleep 5
    done
    echo "Dependencies are ready. Starting up..."
fi

if [ "$1" == "save-dump" ]; then

su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python manage.py force_migrate common && \
    python manage.py force_migrate && \
    python manage.py dump_data --dst-file=fixtures/additional/app-dump.json \
"

elif [ "$1" == "daphne" ]; then

    if [[ -f "/static/vendor/jqwidgets/jqx-all.js" ]]; then
        echo "JQWidgets are bundled within the Contraxsuite Docker image. Not running collectstatic."
    else
        echo "JQWidgets are not bundled within the Docker Image. Checking the volume..."

        JQWIDGETS_ZIP="/third_party_dependencies/jqwidgets.zip"
        if [[ -f "${JQWIDGETS_ZIP}" ]]; then
            echo "Using jqwidgets: ${JQWIDGETS_ZIP}..."
            VENDOR_DIR=/static/vendor
            rm -rf ${VENDOR_DIR}/jqwidgets
            unzip ${JQWIDGETS_ZIP} "jqwidgets/*" -d ${VENDOR_DIR}

            su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && python manage.py collectstatic --noinput"
        else
            echo "Can't find JQWidgets neither in the Docker image nor at ${JQWIDGETS_ZIP}."
            exit 1
        fi
    fi


    cat /build.info > /contraxsuite_services/staticfiles/version.txt
    echo "" >> /contraxsuite_services/staticfiles/version.txt
    cat /build.uuid >> /contraxsuite_services/staticfiles/version.txt

    if [[ -d "/contraxsuite_frontend" && -d "/contraxsuite_frontend_nginx_volume" ]]; then
        echo "Copying embedded frontend files into the shared Nginx volume..."
        echo "Embedded frontend version:"
        cat /contraxsuite_frontend/versionFE.txt
        echo "Embedded frontend build info:"
        cat /contraxsuite_frontend/version.txt
        rm -rf /contraxsuite_frontend_nginx_volume/*
        echo "API_HOST=${DOCKER_DJANGO_HOST_NAME}" > /contraxsuite_frontend/.env
        echo "WS_HOST=${DOCKER_DJANGO_HOST_NAME}" >> /contraxsuite_frontend/.env

        cp -R /contraxsuite_frontend/. /contraxsuite_frontend_nginx_volume/
    fi

    echo "Copying notification templates"
    source /webdav_upload.sh
    upload_files_to_webpath /contraxsuite_services/apps/notifications/notification_templates notification_templates example_ || true

    echo "Ensuring Django superuser is created..."


# Indentation makes sense here
su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python manage.py force_migrate common && \
    python manage.py force_migrate users && \
    python manage.py force_migrate && \
    python manage.py shell -c \"
from apps.deployment.models import Deployment
from apps.deployment.tasks import usage_stats
Deployment.objects.get_or_create(pk=1)
usage_stats.apply()
\" && \
    python manage.py set_site && \
    python manage.py create_superuser --username=Administrator --email=${DOCKER_DJANGO_ADMIN_EMAIL} --password=${DOCKER_DJANGO_ADMIN_PASSWORD} && \
    python manage.py loadnewdata fixtures/common/*.json && \
    python manage.py loadnewdata fixtures/additional/*.json && \
    python manage.py init_app_data --data-dir=/contraxsuite_services/fixtures/demo --upload-dict-data-from-repository && \
    if [ -d fixtures/customer_project ]; then python manage.py loadnewdata fixtures/customer_project/*.json; fi \
"

  if [ "$2" == "shell" ]; then
      /bin/bash
  else
      echo ""
      echo ""
      echo "Starting Daphne at host ${DOCKER_DJANGO_HOST_NAME}..."
      echo ""
      echo ""

      su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
          ulimit -n 65535 && \
          python manage.py check && \
          daphne -b 0.0.0.0 -p 3355 asgi:application"
  fi


elif [ "$1" == "jupyter" ]; then
    echo "Starting Jupyter..."

    VENV_PATH=/contraxsuite_services/venv
    JUPYTER_ADD_REQ_PATH=/contraxsuite_services/jupyter_add_req
    JUPYTER_ADD_REQ=${JUPYTER_ADD_REQ_PATH}/requirements.txt
    JUPYTER_ADD_DEBIAN_REQ=${JUPYTER_ADD_REQ_PATH}/debian-requirements.txt

    mkdir -p ${JUPYTER_ADD_REQ_PATH}

    set +e
    cat ${JUPYTER_ADD_DEBIAN_REQ} | xargs -r apt-get -y -q install
    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && pip install -r ${JUPYTER_ADD_REQ}"
    set -e

    mkdir -p /contraxsuite_services/notebooks
    chown -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /contraxsuite_services/notebooks

    echo "mkdir -p /home/${SHARED_USER_NAME}/.jupyter"
    mkdir -p /home/${SHARED_USER_NAME}/.jupyter
    cat /contraxsuite_services/jupyter_notebook_config.py > /home/${SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py
    chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /home/${SHARED_USER_NAME}/.jupyter

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python -c \"
from notebook.auth import passwd
with open('/home/${SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py', 'a') as myfile:
    myfile.write('\\nc.NotebookApp.password = \'' + passwd('${DOCKER_DJANGO_ADMIN_PASSWORD}') + '\'')
\""
    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        jupyter notebook --port=8888 --no-browser --ip=0.0.0.0"
elif [ $1 == "flower" ]; then
    echo "Starting Flower..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        flower -A apps --port=5555 --address=0.0.0.0 --url_prefix=${DOCKER_FLOWER_BASE_PATH}"
elif [ $1 == "mock-imanage" ]; then
    echo "Starting Mock IManage Server..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        cd apps/imanage_integration/debug/ && \
        python mock_imanage_server.py 65534"
elif [ $1 == "celery-beat" ]; then
    echo "Starting Celery Beat and Serial Tasks Worker..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -B -Q serial --without-gossip --without-heartbeat --concurrency=1 -Ofair -n beat@%h --statedb=/data/celery_worker_state/worker.state --role=beat"
elif [ $1 == "celery-high-prio" ]; then
    echo "Starting Celery High Priority Tasks Worker..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -Q high_priority --without-gossip --without-heartbeat --concurrency=4 -Ofair -n high_priority@%h --statedb=/data/celery_worker_state/worker.state --role=high_prio"

elif [ $1 == "celery-load" ]; then
    echo "Starting Celery Load Documents Tasks Worker..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -Q doc_load --without-gossip --without-heartbeat --concurrency=1 -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state --role=doc_load"

elif [ $1 == "celery-master" ]; then
    echo "Starting Celery Master Low Resources Worker..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -Q default,high_priority --without-gossip --without-heartbeat --concurrency=2 -Ofair -n master@%h --statedb=/data/celery_worker_state/worker.state --role=default_worker"
elif [ $1 == "celery-single" ]; then
    echo "Starting Celery Default Priority Tasks Worker..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        python manage.py check && \
        celery -A apps worker -Q default,high_priority,worker_bcast --without-gossip --without-heartbeat --concurrency=${DOCKER_CELERY_CONCURRENCY} -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state --role=default_worker"
else
    echo "Starting Celery Default Priority Tasks Worker..."

    su ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        python manage.py check && \
        celery -A apps worker -Q default,worker_bcast --without-gossip --without-heartbeat --concurrency=${DOCKER_CELERY_CONCURRENCY} -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state --role=default_worker"
fi
