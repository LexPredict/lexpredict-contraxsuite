#!/bin/bash

export VOLUME_FOLDER="/data/docker/volumes"
export VOLUME_BACKUP_FOLDER="/data/docker_volumes_backup"

set -e

# Check volume folders used space in bytes
VOLUME_USED_SPACE="$(/usr/bin/du -sb $VOLUME_FOLDER | awk '{print $1}')"

# Check backup folders used space in bytes (if applicable)
if [ -d "$VOLUME_BACKUP_FOLDER" ]; then
        VOLUME_BACKUP_USED_SPACE="$(/usr/bin/du -sb $VOLUME_BACKUP_FOLDER | awk '{print $1}')"
else
        VOLUME_BACKUP_USED_SPACE=0
fi

# Check /data volume free space in bytes
DATA_FREE_SPACE="$(/bin/df -B1 | grep /data$ | awk '{print $4}' | cut -f 1 -d '%')"

# Check if DATA_FREE_SPACE + VOLUME_BACKUP_USED_SPACE > VOLUME_USED_SPACE
if [ "$(($DATA_FREE_SPACE + $VOLUME_BACKUP_USED_SPACE))" -gt "$VOLUME_USED_SPACE" ]; then
        /bin/mkdir -p $VOLUME_BACKUP_FOLDER
        /bin/rm -rf $VOLUME_BACKUP_FOLDER/*
        /bin/cp -a $VOLUME_FOLDER/. $VOLUME_BACKUP_FOLDER
fi
