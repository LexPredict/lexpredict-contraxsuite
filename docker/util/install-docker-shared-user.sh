#!/bin/bash

source ../setenv.sh
if [ -e ../setenv_local.sh ]
then
    source ../setenv_local.sh
fi

echo "Contraxsuite Docker container uses a directory shared with host machine for storing uploaded documents."
echo "To allow sharing there should be a user with the same UID at the host machine and Docker container."
echo "Shared user UID is configured to: ${SHARED_USER_ID}"
echo "Shared user name is configured to: ${SHARED_USER_NAME}"

sudo adduser -u ${SHARED_USER_ID} --disabled-password --gecos "" ${SHARED_USER_NAME}

CUR_USER=$(whoami)
echo "Your current user is: ${CUR_USER}"
echo "To allow accessing shared directory for your user it should be added to group ${SHARED_USER_NAME}"
echo    # (optional) move to a new line
sudo usermod -a -G ${SHARED_USER_NAME} ${CUR_USER}