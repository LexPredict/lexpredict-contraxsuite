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

if [ -z "${DOCKER_NGINX_CERTIFICATE}" ]; then
    echo "Embedded Nginx is going to serve plain HTTP."
    envsubst < nginx-http.conf.template > /etc/nginx/conf.d/default.conf
else
    echo "Embedded Nginx is going to serve HTTPS."
    envsubst < nginx-https.conf.template > /etc/nginx/conf.d/default.conf
fi

envsubst < nginx.conf.template > /etc/nginx/nginx.conf
envsubst < nginx-internal.conf.template > /etc/nginx/conf.d/internal.conf
envsubst < run-celery.sh.template > /contraxsuite_services/run-celery.sh
envsubst < run-uwsgi.sh.template > /contraxsuite_services/run-uwsgi.sh
envsubst < local_settings.py.template > /contraxsuite_services/local_settings.py

envsubst < contraxsuite_logstash.conf.template > /etc/logstash/conf.d/contraxsuite_logstash.conf

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



    echo "Collecting DJANGO static files..."
    su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && python manage.py collectstatic --noinput"

    popd

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
    python manage.py shell -c \"
from apps.users.models import User
if not User.objects.filter(username = '${DOCKER_DJANGO_ADMIN_NAME}').exists():
    User.objects.create_superuser('${DOCKER_DJANGO_ADMIN_NAME}', '${DOCKER_DJANGO_ADMIN_EMAIL}', '${DOCKER_DJANGO_ADMIN_PASSWORD}', role='technical_admin')
\""

    if [ $2 == "shell" ]; then
        /bin/bash
    else
        echo "Starting Nginx and Django..."

        #/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/contraxsuite_logstash.conf &

        service nginx start && \
        su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
            ulimit -n 1000000 && \
            python manage.py check && \
            uwsgi --socket 0.0.0.0:3031 \
                    --plugins python3 \
                    --protocol uwsgi \
                    --wsgi wsgi:application" && \
        service nginx stop
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
else
    echo "Sleeping 15 seconds to let Postgres start and Django migrate"
    sleep 15
    echo "Starting Celery..."

    #/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/contraxsuite_logstash.conf &

#    su - ${SHARED_USER_NAME} -c "export LANG=C.UTF-8 && cd /contraxsuite_services && . /contraxsuite_services/venv/bin/activate && \
#        celery worker -A apps --concurrency=2 -B"

#    TASKS=60
#    for i in {1..5};
#    do
#        echo "Attempt #$i";


        su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
            ulimit -n 1000000 && \
            python manage.py check && \
            celery worker -A apps --concurrency=4 -B"
        sleep 20
#        REGISTERED=$(su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
#            celery -A apps inspect registered | grep ' \* ' | wc -l")
#        echo "Registered $REGISTERED tasks"
#        if [ "$REGISTERED" -ne "$TASKS" ]  ; then
#            pkill -f "celery"
#            sleep 10
#        else
#            break
#        fi
#    done
fi
