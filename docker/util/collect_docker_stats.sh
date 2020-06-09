#!/usr/bin/env bash

SOURCE_DIR=~/docker_stats
DEST_DIR=/contraxsuite_services/docker_stats

pushd ..
source setenv.sh
popd

mkdir -p $SOURCE_DIR

DOCKER_SERVICES="$(sudo docker service ls)"
echo "$DOCKER_SERVICES" > $SOURCE_DIR/docker_services_plain.txt
echo "$DOCKER_SERVICES" | cut -c 1-12 | grep -v ID | paste -sd ' ' | xargs -I'SERVICE_ID' sh -c 'sudo docker service inspect SERVICE_ID' > $SOURCE_DIR/docker_services.txt
sudo docker node ls | cut -c 1-24 | grep -v ID | paste -sd ' ' | xargs -I'NODE_ID' sh -c 'sudo docker node inspect NODE_ID' > $SOURCE_DIR/docker_nodes.txt
sudo docker stats --no-stream > $SOURCE_DIR/docker_stats.txt

sudo chown -R $SHARED_USER_ID:$SHARED_USER_ID $SOURCE_DIR
# UWSGI - Daphne migration
TARGET_CONTAINER_ID="$(sudo docker ps --filter "name=-daphne" --format "{{.ID}}")"
sudo docker exec "${TARGET_CONTAINER_ID}" sh -c "mkdir -p $DEST_DIR"
sudo docker cp $SOURCE_DIR/. $TARGET_CONTAINER_ID:$DEST_DIR

sudo rm -r $SOURCE_DIR
