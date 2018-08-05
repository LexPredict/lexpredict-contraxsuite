#!/usr/bin/env bash

pushd ../

source setenv.sh

if [ "$DOCKER_DIR" != "/var/lib/docker" ]; then
  sudo service docker stop

  sudo mkdir -p ${DOCKER_DIR}
  sudo sed -i "/ExecStart/c\ExecStart=/usr/bin/dockerd -g $DOCKER_DIR -H fd://" /lib/systemd/system/docker.service
  sudo systemctl daemon-reload

  sudo service docker start
fi
