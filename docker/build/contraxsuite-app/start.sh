#!/bin/bash

set -e

IMAGE_UUID_FILE=/build.uuid
DEPLOYMENT_UUID_FILE=/deployment_uuid/deployment.uuid
PROJECT_DIR="/contraxsuite_services"
VENV_PATH="/contraxsuite_services/venv/bin/activate"
ACTIVATE_VENV="export LANG=C.UTF-8 && cd ${PROJECT_DIR} && . ${VENV_PATH} "

echo ""
echo ===================================================================
cat /build.info
echo "Build UUID:"
cat ${IMAGE_UUID_FILE}
if [ -e ${DEPLOYMENT_UUID_FILE} ]; then
    echo "Deployment UUID: $(cat ${DEPLOYMENT_UUID_FILE})"
else
    echo "Deployment UUID not stored yet"
fi
echo "Going to start: $1..."
echo ===================================================================
echo ""

echo "Adding Docker <-> Host shared user..."
if ! adduser -u ${SHARED_USER_ID} --disabled-password --gecos "" ${SHARED_USER_NAME} ; then
    echo "Shared user already exists: ${SHARED_USER_NAME} (${SHARED_USER_ID})"
fi

echo "Adding Docker Shared User to root group..."
usermod -a -G root ${SHARED_USER_NAME}


echo "Creating data dirs..."
mkdir -p /data/data
mkdir -p /data/logs
mkdir -p /data/celery_worker_state
mkdir -p /data/media/data/documents
mkdir -p $(dirname ${DEPLOYMENT_UUID_FILE})

echo "Configuring permissions..."
chown -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /contraxsuite_services || true
chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /contraxsuite_services/staticfiles || true
chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /data || true
chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /static || true
chmod -R -v ug+rw /data/media/data/documents || true


echo "Preparing configuration based on env variables..."
pushd /config-templates

export DOLLAR='$' # escape $ in envsubst

envsubst < run-celery.sh.template > /contraxsuite_services/run-celery.sh
envsubst < run-uwsgi.sh.template > /contraxsuite_services/run-uwsgi.sh
envsubst < local_settings.py.template > /contraxsuite_services/local_settings.py

chmod ug+x /contraxsuite_services/run-celery.sh
chmod ug+x /contraxsuite_services/run-uwsgi.sh

popd


echo "Preparing NLTK data..."
chown -R ${SHARED_USER_NAME}:${SHARED_USER_NAME} /root/nltk_data
mv /root/nltk_data /home/${SHARED_USER_NAME}/
echo =======NLTK======
ls -lL /home/${SHARED_USER_NAME}/nltk_data
echo =================

pushd /contraxsuite_services

if [ $1 == "uwsgi" ]; then
    echo "Preparing theme..."
    THEME_ZIP=/third_party_dependencies/$(basename ${DOCKER_DJANGO_THEME_ARCHIVE})
    THEME_DIR=/static/theme
    rm -rf ${THEME_DIR}
    mkdir -p ${THEME_DIR}
    unzip ${THEME_ZIP} "Package-HTML/HTML/js/*" -d ${THEME_DIR}
    unzip ${THEME_ZIP} "Package-HTML/HTML/css/*" -d ${THEME_DIR}
    unzip ${THEME_ZIP} "Package-HTML/HTML/images/*" -d ${THEME_DIR}
    unzip ${THEME_ZIP} "Package-HTML/HTML/style.css" -d ${THEME_DIR}
    mv ${THEME_DIR}/Package-HTML/HTML/js ${THEME_DIR}/
    mv ${THEME_DIR}/Package-HTML/HTML/css ${THEME_DIR}/
    mv ${THEME_DIR}/Package-HTML/HTML/images ${THEME_DIR}/
    mv ${THEME_DIR}/Package-HTML/HTML/style.css ${THEME_DIR}/css/

    echo "Preparing jqwidgets..."
    JQWIDGETS_ZIP=/third_party_dependencies/$(basename ${DOCKER_DJANGO_JQWIDGETS_ARCHIVE})
    VENDOR_DIR=/static/vendor
    rm -rf ${VENDOR_DIR}/jqwidgets
    unzip ${JQWIDGETS_ZIP} "jqwidgets/*" -d ${VENDOR_DIR}

    cat /build.info > /contraxsuite_services/staticfiles/version.txt
    echo "" >> /contraxsuite_services/staticfiles/version.txt
    cat /build.uuid >> /contraxsuite_services/staticfiles/version.txt

    # Put this build uuid to a persistent storage to avoid running preparation procedures again
    # (see start of this script)
    cat ${IMAGE_UUID_FILE} > ${DEPLOYMENT_UUID_FILE}

    echo "Sleeping 5 seconds to let Postgres start"
    sleep 5

    while ! curl http://${DOCKER_HOST_NAME_PG}:5432/ 2>&1 | grep '52'
    do
      echo "Sleeping 5 seconds to let Postgres start"
      sleep 5
    done

    echo "Ensuring Django superuser is created..."

# Indentation makes sense here
su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python manage.py force_migrate && \
    python manage.py collectstatic --noinput && \
    python manage.py set_site && \
    python manage.py create_superuser --username=${DOCKER_DJANGO_ADMIN_NAME} --email=${DOCKER_DJANGO_ADMIN_EMAIL} --password=${DOCKER_DJANGO_ADMIN_PASSWORD} && \
    python manage.py loadnewdata fixtures/common/*.json && \
    python manage.py loadnewdata fixtures/private/*.json
"

    if [ $2 == "shell" ]; then
        /bin/bash
    else
        echo "Starting Django..."

        su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
            ulimit -n 1000000 && \
            python manage.py check && \
            uwsgi --socket 0.0.0.0:3031 \
                    --plugins python3 \
                    --protocol uwsgi \
                    --wsgi wsgi:application"
    fi
elif [ $1 == "jupyter" ]; then
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Jupyter..."

    mkdir -p /contraxsuite_services/notebooks
    chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /contraxsuite_services/notebooks

    mkdir -p /home/${SHARED_USER_NAME}/.jupyter
    envsubst < /config-templates/jupyter_notebook_config.py.template > /home/${SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py
    chown -R -v ${SHARED_USER_NAME}:${SHARED_USER_NAME} /home/${SHARED_USER_NAME}/.jupyter

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    python -c \"
from notebook.auth import passwd
with open('/home/${SHARED_USER_NAME}/.jupyter/jupyter_notebook_config.py', 'a') as myfile:
    myfile.write('\\nc.NotebookApp.password = \'' + passwd('${DOCKER_DJANGO_ADMIN_PASSWORD}') + '\'')
\""
    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 1000000 && \
        jupyter notebook --port=8888 --no-browser --ip=0.0.0.0"
elif [ $1 == "flower" ]; then
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Flower..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 1000000 && \
        flower -A apps --port=5555 --address=0.0.0.0 --url_prefix=${DOCKER_FLOWER_BASE_PATH}"
elif [ $1 == "celery-beat" ]; then
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Celery Beat and Serial Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 1000000 && \
        celery -A apps worker -B -Q serial --concurrency=1 -Ofair -n beat@%h --statedb=/data/celery_worker_state/worker.state"
elif [ $1 == "celery-high-prio" ]; then
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Celery High Priority Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 1000000 && \
        celery -A apps worker -Q high_priority --concurrency=4 -Ofair -n high_priority@%h --statedb=/data/celery_worker_state/worker.state"
elif [ $1 == "celery-master" ]; then
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Celery Master Low Resources Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 1000000 && \
        celery -A apps worker -Q default,high_priority --concurrency=2 -Ofair -n master@%h --statedb=/data/celery_worker_state/worker.state"
else
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Celery Default Priority Tasks Worker..."

    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
        ulimit -n 1000000 && \
        python manage.py check && \
        celery -A apps worker -Q default,high_priority --concurrency=4 -Ofair -n default_priority@%h --statedb=/data/celery_worker_state/worker.state"
    sleep 20
fi
