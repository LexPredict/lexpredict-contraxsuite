#!/bin/bash

set -e

CPU_CORES=${DOLLAR}(grep -c ^processor /proc/cpuinfo)
CPU_QUARTER_CORES=${DOLLAR}(( ${DOLLAR}{CPU_CORES} > 4 ? ${DOLLAR}{CPU_CORES} / 4 : 1 ))
SHARED_USER_NAME=${DOLLAR}(whoami)
ROLE=${DOLLAR}1

echo ""
echo ===================================================================
echo "Contraxsuite"
echo "Build info:"
cat /build.info
echo "Build UUID:"
cat /build.uuid
echo "Going to start: ${DOLLAR}{ROLE}..."
echo "Python version:"
python3 --version
echo ""
echo ===================================================================
echo ""


function wait_for_deps () {
  echo "Starting: ${DOLLAR}{ROLE}"
  echo "Working as user: ${DOLLAR}{SHARED_USER_NAME} (id=${DOLLAR}(id -u ${DOLLAR}{SHARED_USER_NAME}))"
  if [[ -z "${DOLLAR}{STARTUP_DEPS_READY_CMD}" ]]; then
      echo "No dependencies specified to wait. Starting up..."
  else
      echo "Dependencies readiness test command: ${DOLLAR}{STARTUP_DEPS_READY_CMD}"
      while ! eval ${DOLLAR}{STARTUP_DEPS_READY_CMD}
      do
        echo "Dependencies are not ready. Waiting 5 seconds..."
        sleep 5
      done
      echo "Dependencies are ready. Starting up..."
  fi
  ulimit -n 65535
}

function startup () {
  wait_for_deps
  python3 manage.py check && echo "System is consistent." || exit 1
}

if [ "${DOLLAR}{ROLE}" == "save-dump" ]; then
    startup
    python3 manage.py migrate && \
    python3 manage.py dump_data --dst-file=fixtures/additional/app-dump.json && \
    python3 manage.py init_cache

elif [ "${DOLLAR}{ROLE}" == "unit_tests" ]; then
    echo "SECRET_KEY = str(1)" >> local_settings.py
    startup
    cp -rn /home/contraxsuite_docker_user/nltk_data /root
    exec python3 manage.py test --settings=nodb_settings

elif [ "${DOLLAR}{ROLE}" == "daphne" ]; then
    wait_for_deps

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


    mkdir -p /contraxsuite_services/staticfiles
    cat /build.info > /contraxsuite_services/staticfiles/version.txt
    echo "" >> /contraxsuite_services/staticfiles/version.txt
    cat /build.uuid >> /contraxsuite_services/staticfiles/version.txt
    echo "" >> /contraxsuite_services/staticfiles/version.txt
    cat /build_info.txt >> /contraxsuite_services/staticfiles/version.txt


    if [[ -d "/contraxsuite_frontend" && -d "/contraxsuite_frontend_nginx_volume" ]]; then
        echo "Copying embedded frontend files into the shared Nginx volume..."
        echo "Embedded frontend version:"
        cat /contraxsuite_frontend/versionFE.txt
        echo ""
        echo "Embedded frontend build info:"
        cat /contraxsuite_frontend/version.txt
        echo ""
        rm -rf /contraxsuite_frontend_nginx_volume/*
        echo "API_HOST=${DOLLAR}{DOCKER_DJANGO_HOST_NAME}" > /contraxsuite_frontend/.env
        echo "WS_HOST=${DOLLAR}{DOCKER_DJANGO_HOST_NAME}" >> /contraxsuite_frontend/.env

        cp -R /contraxsuite_frontend/. /contraxsuite_frontend_nginx_volume/
    fi

    echo "Copying notification templates"
    source /webdav_upload.sh
    upload_files_to_webpath /contraxsuite_services/apps/notifications/notification_templates notification_templates example_ || true

    echo "Ensuring Django superuser is created..."

    python3 manage.py migrate

    python3 manage.py check && echo "System is consistent." || exit 1

    # Indentation makes sense here
    python3 manage.py shell -c "
from apps.deployment.models import Deployment
from apps.deployment.tasks import usage_stats
Deployment.objects.get_or_create(pk=1)
usage_stats.apply()
" && \
    python3 manage.py set_site && \
    python3 manage.py loadnewdata fixtures/common/*.json && \
    python3 manage.py loadnewdata fixtures/additional/*.json && \
    python3 manage.py create_superuser --username=Administrator --email=${DOLLAR}{DOCKER_DJANGO_ADMIN_EMAIL} --password=${DOLLAR}{DOCKER_DJANGO_ADMIN_PASSWORD} && \
    python3 manage.py init_app_vars && \
    python3 manage.py init_app_data --data-dir=/contraxsuite_services/fixtures/demo --upload-dict-data-from-repository && \
    python3 manage.py download_s3_models && \
    if [ -d fixtures/customer_project ]; then python3 manage.py loadnewdata fixtures/customer_project/*.json; fi

    echo ""
    echo ""
    echo "Starting Daphne at host ${DOLLAR}{DOCKER_DJANGO_HOST_NAME}..."
    echo ""
    echo ""

    exec daphne -b 0.0.0.0 -p 3355 asgi:application


elif [ "${DOLLAR}{ROLE}" == "jupyter" ]; then
    startup
    echo "Starting Jupyter..."

    JUPYTER_ADD_REQ_PATH=/contraxsuite_services/jupyter_add_req
    JUPYTER_ADD_REQ=${DOLLAR}{JUPYTER_ADD_REQ_PATH}/requirements.txt
    JUPYTER_ADD_DEBIAN_REQ=${DOLLAR}{JUPYTER_ADD_REQ_PATH}/debian-requirements.txt

    mkdir -p ${DOLLAR}{JUPYTER_ADD_REQ_PATH}

    set +e
    cat ${DOLLAR}{JUPYTER_ADD_DEBIAN_REQ} | xargs -r apt-get -y -q install
    pip3 install -r ${DOLLAR}{JUPYTER_ADD_REQ}
    set -e

    mkdir -p /contraxsuite_services/notebooks
    chown -v ${DOLLAR}{SHARED_USER_NAME}:${DOLLAR}{SHARED_USER_NAME} /contraxsuite_services/notebooks

    echo "mkdir -p /home/${DOLLAR}{SHARED_USER_NAME}/.jupyter"
    mkdir -p /home/${DOLLAR}{SHARED_USER_NAME}/.jupyter
    cat /contraxsuite_services/jupyter_notebook_config.py > /home/${DOLLAR}{SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py
    chown -R -v ${DOLLAR}{SHARED_USER_NAME}:${DOLLAR}{SHARED_USER_NAME} /home/${DOLLAR}{SHARED_USER_NAME}/.jupyter

    python3 -c "
from notebook.auth import passwd
with open('/home/${DOLLAR}{SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py', 'a') as myfile:
    myfile.write('\\nc.NotebookApp.password = \'' + passwd('${DOLLAR}{DOCKER_DJANGO_ADMIN_PASSWORD}') + '\'')
"
    exec jupyter notebook --port=8888 --no-browser --ip=0.0.0.0
elif [ "${DOLLAR}{ROLE}" == "flower" ]; then
    startup
    echo "Starting Flower..."
    exec flower -A apps --port=5555 --address=0.0.0.0 --url_prefix=${DOLLAR}{DOCKER_FLOWER_BASE_PATH}
elif [ "${DOLLAR}{ROLE}" == "mock-imanage" ]; then
    startup
    echo "Starting Mock IManage Server..."
    cd apps/imanage_integration/debug/
    exec python3 mock_imanage_server.py 65534
elif [ "${DOLLAR}{ROLE}" == "celery-beat" ]; then
    startup
    echo "Starting Celery Beat and Serial Tasks Worker..."
    exec celery -A apps worker -B -Q serial --concurrency=1 -Ofair -n beat@%h --statedb=/data/celery_worker_state/celery-beat.state --role=beat
elif [ "${DOLLAR}{ROLE}" == "celery-high-prio" ]; then
    startup
    echo "Starting Celery High Priority Tasks Worker..."
    exec celery -A apps worker -Q high_priority --concurrency=4 --autoscale=4,4 -Ofair -n high_priority@%h --statedb=/data/celery_worker_state/celery-high-prio.state --role=high_prio
elif [ "${DOLLAR}{ROLE}" == "celery-master" ]; then
    startup
    echo "Starting Celery Master Low Resources Worker..."
    exec celery -A apps worker -Q default,high_priority --concurrency=2 --autoscale=2,2 -Ofair -n master@%h --statedb=/data/celery_worker_state/celery-master.state --role=default_worker
elif [ "${DOLLAR}{ROLE}" == "celery-single" ]; then
    startup
    echo "Starting Celery Default Priority Tasks Worker..."
    exec celery -A apps worker -Q default,high_priority,worker_bcast --concurrency=${DOLLAR}{DOCKER_CELERY_CONCURRENCY} --autoscale=${DOLLAR}{DOCKER_CELERY_CONCURRENCY},${DOLLAR}{DOCKER_CELERY_CONCURRENCY}  -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/celery-single.state --role=default_worker
elif [ "${DOLLAR}{ROLE}" == "celery" ]; then
    startup
    echo "Starting Celery Default Priority Tasks Worker..."
    exec celery -A apps worker -Q default,worker_bcast --concurrency=${DOLLAR}{DOCKER_CELERY_CONCURRENCY} --autoscale=${DOLLAR}{DOCKER_CELERY_CONCURRENCY},${DOLLAR}{DOCKER_CELERY_CONCURRENCY} -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/celery-default-prio.state --role=default_worker
elif [ "${DOLLAR}{ROLE}" == "shell" ]; then
    exec /bin/bash
else
    startup
    echo "Starting Bash..."
    exec /bin/bash
fi
