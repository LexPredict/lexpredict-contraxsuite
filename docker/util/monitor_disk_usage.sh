#!/usr/bin/env bash

pushd ..
source setenv.sh
popd

DISK_USAGE_PCNT="$(sudo df /data --output=pcent | tr -dc '0-9')"
FREE_DISK_GB="$(sudo df /data -BG --output=avail | tr -dc '0-9')"

PG_CONTAINER_ID="$(sudo docker ps --filter "volume=/backup" --format "{{.ID}}")"

PG_COMMAND_DISK_USAGE="UPDATE common_appvar SET value='$DISK_USAGE_PCNT', date=now() WHERE name='disk_usage'"
PG_COMMAND_FREE_DISK="UPDATE common_appvar SET value='$FREE_DISK_GB', date=now() WHERE name='free_disk'"

sudo docker exec "${PG_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U $DOCKER_PG_USER -d $DOCKER_PG_DB_NAME -c \"${PG_COMMAND_DISK_USAGE}\""
sudo docker exec "${PG_CONTAINER_ID}" sh -c "PGPASSWORD=$DOCKER_PG_PASSWORD /usr/bin/psql -U $DOCKER_PG_USER -d $DOCKER_PG_DB_NAME -c \"${PG_COMMAND_FREE_DISK}\""
