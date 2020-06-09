#!/bin/bash

set -e
source /webdav_upload.sh

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

su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python manage.py force_migrate common && \
    python manage.py force_migrate && \
    python manage.py dump_data --dst-file=fixtures/additional/app-dump.json \
"

elif [ "$1" == "daphne" ]; then

    echo "Preparing jqwidgets..."
    JQWIDGETS_ZIP=/third_party_dependencies/$(basename ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE})
    VENDOR_DIR=/static/vendor
    rm -rf ${VENDOR_DIR}/jqwidgets
    unzip ${JQWIDGETS_ZIP} "jqwidgets/*" -d ${VENDOR_DIR}

    echo "Updating customizable notification templates in media folder..."
    cat /build.info > /contraxsuite_services/staticfiles/version.txt
    echo "" >> /contraxsuite_services/staticfiles/version.txt
    cat /build.uuid >> /contraxsuite_services/staticfiles/version.txt

    echo "Copying notification templates"
    upload_files_to_webpath /contraxsuite_services/apps/notifications/notification_templates notification_templates example_ || true

    echo "Ensuring Django superuser is created..."


# Indentation makes sense here
su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python manage.py force_migrate common && \
    python manage.py force_migrate users && \
    python manage.py force_migrate && \
    python manage.py shell -c \"
from apps.deployment.models import Deployment
from apps.deployment.tasks import usage_stats
Deployment.objects.get_or_create(pk=1)
usage_stats.apply()
\" && \
    python manage.py collectstatic --noinput && \
    python manage.py set_site && \
    python manage.py create_superuser --username=${DOCKER_DJANGO_ADMIN_NAME} --email=${DOCKER_DJANGO_ADMIN_EMAIL} --password=${DOCKER_DJANGO_ADMIN_PASSWORD} && \
    python manage.py loadnewdata fixtures/common/*.json && \
    python manage.py loadnewdata fixtures/additional/*.json && \
    python manage.py init_app_data --data-dir=/data/data_update --arch-files && \
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

      su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
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
    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && pip install -r ${JUPYTER_ADD_REQ}"
    set -e

    mkdir -p /contraxsuite_services/notebooks
    chown -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /contraxsuite_services/notebooks

    echo "mkdir -p /home/${SHARED_USER_NAME}/.jupyter"
    mkdir -p /home/${SHARED_USER_NAME}/.jupyter
    cat /contraxsuite_services/jupyter_notebook_config.py > /home/${SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py
    chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /home/${SHARED_USER_NAME}/.jupyter

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python -c \"
from notebook.auth import passwd
with open('/home/${SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py', 'a') as myfile:
    myfile.write('\\nc.NotebookApp.password = \'' + passwd('${DOCKER_DJANGO_ADMIN_PASSWORD}') + '\'')
\""
    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        jupyter notebook --port=8888 --no-browser --ip=0.0.0.0"
elif [ $1 == "flower" ]; then
    echo "Starting Flower..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        flower -A apps --port=5555 --address=0.0.0.0 --url_prefix=${DOCKER_FLOWER_BASE_PATH}"
elif [ $1 == "celery-beat" ]; then
    echo "Starting Celery Beat and Serial Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -B -Q serial --without-gossip --without-heartbeat --concurrency=1 -Ofair -n beat@%h --statedb=/data/celery_worker_state/worker.state --role=beat"
elif [ $1 == "celery-high-prio" ]; then
    echo "Starting Celery High Priority Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -Q high_priority --without-gossip --without-heartbeat --concurrency=4 -Ofair -n high_priority@%h --statedb=/data/celery_worker_state/worker.state --role=high_prio"

elif [ $1 == "celery-load" ]; then
    echo "Starting Celery Load Documents Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -Q doc_load --without-gossip --without-heartbeat --concurrency=1 -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state --role=doc_load"

elif [ $1 == "celery-master" ]; then
    echo "Starting Celery Master Low Resources Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        celery -A apps worker -Q default,high_priority --without-gossip --without-heartbeat --concurrency=2 -Ofair -n master@%h --statedb=/data/celery_worker_state/worker.state --role=default_worker"
elif [ $1 == "celery-single" ]; then
    echo "Starting Celery Default Priority Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        python manage.py check && \
        celery -A apps worker -Q default,high_priority --without-gossip --without-heartbeat --concurrency=${DOCKER_CELERY_CONCURRENCY} -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state --role=default_worker"
else
    echo "Starting Celery Default Priority Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 65535 && \
        python manage.py check && \
        celery -A apps worker -Q default --without-gossip --without-heartbeat --concurrency=${DOCKER_CELERY_CONCURRENCY} -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state --role=default_worker"
fi
