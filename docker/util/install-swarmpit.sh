#!/bin/bash

TMP=/var/tmp/$(uuidgen)
mkdir -p ${TMP}

pushd ${TMP}
git clone https://github.com/swarmpit/swarmpit -b 1.2
sudo docker stack deploy -c swarmpit/docker-compose.yml swarmpit
popd

rm -rf ${TMP}