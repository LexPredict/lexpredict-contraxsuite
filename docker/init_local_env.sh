#!/usr/bin/env bash

export SETENV_LOCAL=setenv_local.sh
source setenv.sh
if [ -e setenv_local.sh ]
then
    source setenv_local.sh
fi

SAVED_VARIABLES=()

store_variable() {
    NAME=$1
    VALUE=$2
    if [ -e setenv_local.sh ]; then
        sed -i "/${NAME}/d" ${SETENV_LOCAL}
    fi
    echo "export ${NAME}=${VALUE}" >> ${SETENV_LOCAL}
    SAVED_VARIABLES+=(${NAME})
}

init_variable() {
    NAME=$1
    DEFAULT_VALUE=${!NAME}
    TITLE=$2
    echo -n "Enter your ${TITLE}, current value is ${DEFAULT_VALUE}, press enter or input new value: "
    read VALUE
    if [ ! -z ${VALUE} ]; then
        store_variable ${NAME} ${VALUE}
    else
        SAVED_VARIABLES+=(${NAME})
    fi
}

init_variable "DOCKER_DJANGO_HOST_NAME" "domain name"
init_variable "DOCKER_DIR" "docker dir"

export DOCKER_COMPOSE_FILE=unset

while [ "unset" == "${DOCKER_COMPOSE_FILE}" ]
do
    echo -n "Select cluster configuration: \
1: everything on single host \
2: single master + many workers (possibly with auto-scaling) \
"
    read CLUSTER_CONFIG_NUM
    if [ "${CLUSTER_CONFIG_NUM}" == "1" ]; then
        export DOCKER_COMPOSE_FILE=docker-compose-single-host.yml
    elif [ "${CLUSTER_CONFIG_NUM}" == "2" ]; then
        export DOCKER_COMPOSE_FILE=docker-compose-single-master-many-workers.yml
    fi
done

echo "Proceeding with docker-compose file: ${DOCKER_COMPOSE_FILE}"

store_variable "DOCKER_COMPOSE_FILE" ${DOCKER_COMPOSE_FILE}
store_variable "DOLLAR" "$"
store_variable "DOCKER_DJANGO_BASE_PATH" "/advanced/"
store_variable "DOCKER_KIBANA_BASE_PATH" "/kibana"

echo""
echo "Local environment:"
echo ""

source setenv_local.sh
for VARIABLE_NAME in ${SAVED_VARIABLES[@]}; do
    echo "${VARIABLE_NAME}: ${!VARIABLE_NAME}"
done

echo ""

popd
