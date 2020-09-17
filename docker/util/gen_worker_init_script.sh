#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./generate_worker_init_script.sh output_file.sh"
    exit 1
fi

pushd ..
source setenv.sh
popd

export DOCKER_SWARM_JOIN_TOKEN=$(sudo docker swarm join-token -q worker)
export DOCKER_SWARM_MASTER_IP=$(sudo docker node inspect self --format '{{ .Status.Addr  }}')

if [[ "${CHANGE_APT_SOURCES_TO_HTTPS,,}" = 'true' ]]; then
    export SCRIPT_CHANGE_APT_SOURCES_TO_HTTPS=$(sed '1d' change_apt_sources_to_https.sh)
else
    export SCRIPT_CHANGE_APT_SOURCES_TO_HTTPS=
fi

export SCRIPT_CONFIGURE_HOST=$(sed '1d' configure_host.sh)
export SCRIPT_INSTALL_DOCKER=$(sed '1d' install-docker-ubuntu.sh)

envsubst < worker-init-script.sh.template > $1
