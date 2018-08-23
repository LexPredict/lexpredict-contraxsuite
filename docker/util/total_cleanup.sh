#!/usr/bin/env bash

echo -n "Are you sure to delete all data from the database (type whole word - yes/no)? \
"
read CONFIRMATION

if [ "yes" != "${CONFIRMATION}" ]; then
    exit
fi

set -e
pushd ..
source setenv.sh
source volumes.sh
popd

echo "Dumping data to json fixture..."
sudo ./docker-exec.sh contraxsuite_contrax-uwsgi 1 ./dump.sh

echo "Stopping Docker..."
sudo service docker stop
echo "Deleting Postgres, RabbitMQ and Celery Worker State Volumes to cleanup tasks"
sudo rm -rf `sudo realpath ${VOLUME_RABBIT}/..`
sudo rm -rf `sudo realpath ${VOLUME_CELERY_WORK_STATE}/..`
sudo rm -rf `sudo realpath ${VOLUME_DB}/..`
sudo rm -rf ${VOLUME_DATA_MEDIA}/data/documents/*

echo "Postgres volume has been deleted on this local machine."
echo "If Postgres is running on another machine - please delete its volume manually NOW."
echo "Type 'done' when ready..."

export DONE=nothing

while [ "done" != "${DONE}" ]
do
    read DONE
done

echo "Starting Docker - it will reload the data from the fixture..."
sudo service docker start

echo "Done."

