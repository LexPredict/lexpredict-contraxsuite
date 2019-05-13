#!/usr/bin/env bash

pushd ../

source volumes.sh
source setenv.sh

export REMOTE_DESTINATION=$1
export REMOTE_USER=$2
export SLACK_WEBHOOK=$3

DOCKER_BACKUP_FOLDER=/data/docker/volumes/contraxsuite_backup/_data/db

clean_daily_backups() {
	# Check if the newest backup was created on Sunday
	DAY_OF_WEEK="$(/usr/bin/basename $file | cut -f 2 -d '_' | { read backup_date ; date +%A -d "$backup_date" ; })"
	# If the newest backup was created on Sunday, move it to the weekly backups folder.
	if [ $DAY_OF_WEEK == 'Sunday' ]
	then
		/usr/bin/sudo -u $REMOTE_USER bash -c "mv -f $REMOTE_DESTINATION/daily_database_backups/"$(/usr/bin/basename $file)" $REMOTE_DESTINATION/weekly_database_backups"
	fi
	# Make sure only 7 daily backups are left
	( cd $REMOTE_DESTINATION/daily_database_backups/ ; /bin/ls -1tr $REMOTE_DESTINATION/daily_database_backups/ | head -n -7 | xargs -d '\n' rm -f -- )
}

notify_on_slack() {
	case $1 in
		0)
			/usr/bin/curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Postgres backup bot\", \"text\": \"There was a problem with backing up Postgres database for ${DOCKER_DJANGO_HOST_NAME}.\", \"icon_emoji\": \":thumbsdown:\"}" $SLACK_WEBHOOK
			;;
                1)
                        /usr/bin/curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Postgres backup bot\", \"text\": \"Postgres database for ${DOCKER_DJANGO_HOST_NAME} has been successfully backed up.\", \"icon_emoji\": \":ok_hand:\"}" $SLACK_WEBHOOK
                        ;;
                2)
                        /usr/bin/curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Postgres backup bot\", \"text\": \"Postgres database backup for ${DOCKER_DJANGO_HOST_NAME} failed - system not able to store even one weekly backup. Address immediately!\", \"icon_emoji\": \":thumbsdown:\"}" $SLACK_WEBHOOK
                        ;;
		*)
			echo "Wrong variable" || notify_on_slack 0
			;;
	esac
}

# Execute the backup script inside the container
POSTGRES_CONTAINER_ID="$(sudo docker ps --filter "volume=/backup" --format "{{.ID}}")"
/usr/bin/sudo docker exec "${POSTGRES_CONTAINER_ID}" sh -c "/bin/bash /contraxsuite/db-backup.sh" || notify_on_slack 0

# Find the newest backup file in the folder
for file in "$DOCKER_BACKUP_FOLDER"/*; do
  [[ $file -nt $latest ]] && latest=$file
done

# Check new backup files size in a temporary folder (in bytes)
NEW_BACKUP_SIZE="$(/bin/ls -ln $file | awk '{print $5}')"

# Remove trailing slash from REMOTE_DESTINATION if needed
REMOTE_DESTINATION="$(echo $REMOTE_DESTINATION | sed 's/\/$//')"

# Create folders for daily and weekly backups if needed
/usr/bin/sudo -u $REMOTE_USER bash -c "mkdir -p $REMOTE_DESTINATION/daily_database_backups" || notify_on_slack 0
/usr/bin/sudo -u $REMOTE_USER bash -c "mkdir -p $REMOTE_DESTINATION/weekly_database_backups" || notify_on_slack 0

# Find the backup volume descriptor
BACKUP_DISK_DESCRIPTOR="$(/bin/df | grep "$REMOTE_DESTINATION$" | awk '{print $1}')"

# Check if there is enough free space on the external mount point (in bytes)
EXTERNAL_MOUNT_FREE_SPACE="$(/bin/df -B1 | grep $BACKUP_DISK_DESCRIPTOR | awk '{print $4}')"

# TESTING: HARDCODING FREE SPACE VALUE
#EXTERNAL_MOUNT_FREE_SPACE=500000

# If there is enough space on external storage, copy the new backup file.
if [ $EXTERNAL_MOUNT_FREE_SPACE -gt $NEW_BACKUP_SIZE ]
then
	# There is enough space on external backup. Copying file.
	# Copy the most recent backup file to external mount point
	/usr/bin/sudo -u $REMOTE_USER bash -c "mv -f $file $REMOTE_DESTINATION/daily_database_backups/" || notify_on_slack 0
	# Check if file has been moved correctly and send appropriate Slack message
	/bin/ls $REMOTE_DESTINATION/daily_database_backups/"$(basename $file)" && notify_on_slack 1 || notify_on_slack 0
	clean_daily_backups || notify_on_slack 0
else
	# There is not enough space available. Executing retention management process.
	while [ $EXTERNAL_MOUNT_FREE_SPACE -lt $NEW_BACKUP_SIZE ]
	do
		# Remove oldest weekly backup available
		/bin/rm "$REMOTE_DESTINATION/weekly_database_backups/$(ls -t $REMOTE_DESTINATION/weekly_database_backups | tail -1)" || notify_on_slack 2
		EXTERNAL_MOUNT_FREE_SPACE="$(/bin/df -B1 | grep $BACKUP_DISK_DESCRIPTOR | awk '{print $4}')"
	done
	# After enough space is recovered copy the most recent backup file to external mount point
	/usr/bin/sudo -u $REMOTE_USER bash -c "mv -f $file $REMOTE_DESTINATION/daily_database_backups/" && notify_on_slack 1 || notify_on_slack 0
	clean_daily_backups || notify_on_slack 0
fi

# Remove all old backups from temporary folder
/bin/rm -f $DOCKER_BACKUP_FOLDER/* || notify_on_slack 0