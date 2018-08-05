#!/bin/bash


PROJECT_DIR="/contraxsuite_services"
VENV_PATH="/contraxsuite_services/venv/bin/activate"
ACTIVATE_VENV="export LANG=C.UTF-8 && cd ${PROJECT_DIR} && . ${VENV_PATH} "
TASKS=60

REGISTERED=$(su - ${SHARED_USER_NAME} -c "${ACTIVATE_VENV} && \
    celery -A apps inspect registered | grep ' \* ' | wc -l")

echo "Registered $REGISTERED tasks"

if [ "$REGISTERED" -ne "$TASKS" ]  ; then
    exit 1
else
    exit 0
fi
