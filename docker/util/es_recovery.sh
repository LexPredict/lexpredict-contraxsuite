#!/bin/bash

pushd ../

source volumes.sh
source setenv.sh

export SLACK_WEBHOOK=$1

notify_on_slack() {
	case $1 in
                1)
                        /usr/bin/curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Elasticsearch recovery bot\", \"text\": \"Elasticsearch indexes on ${DOCKER_DJANGO_HOST_NAME} have been unlocked from the read only mode.\", \"icon_emoji\": \":ok_hand:\"}" $SLACK_WEBHOOK
                        ;;
                2)
                        /usr/bin/curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Elasticsearch recovery bot\", \"text\": \"Elasticsearch indexes on ${DOCKER_DJANGO_HOST_NAME} are in the read only mode and there is no enough space to recover. Address immediately!\", \"icon_emoji\": \":thumbsdown:\"}" $SLACK_WEBHOOK
                        ;;
		*)
			echo "Wrong variable"
			;;
	esac
}

# Find Elasticsearch container and Filebeat services IDs
ELASTICSEARCH_CONTAINER_ID="$(docker ps --filter "name=contraxsuite_contrax-elasticsearch" --format "{{.ID}}")"
FILEBEAT_SERVICE_ID="$(docker service ls --filter "name=contraxsuite_contrax-filebeat" --format "{{.ID}}")"

# Download current indexes settings
docker exec "${ELASTICSEARCH_CONTAINER_ID}" sh -c "curl -X GET http://localhost:9200/_settings" > /tmp/escurloutput

# Check data folders used space in percents
DATA_USED_SPACE="$(/bin/df -B1 | grep /data$ | awk '{print $5}' | cut -f 1 -d '%')"

# Check if read only mode is enabled and if free disk space is at least 5%
if grep -q read_only_allow_delete "/tmp/escurloutput" && [[ "$DATA_USED_SPACE" -lt 95 ]]; then
	# If both conditions are met, unblock Elasticsearch indexes and send Slack message
	docker exec "${ELASTICSEARCH_CONTAINER_ID}" sh -c "curl -XPUT -H \"Content-Type: application/json\" \
	http://localhost:9200/_all/_settings \
	-d '{\"index.blocks.read_only_allow_delete\": null}'"
	notify_on_slack 1
fi

# Check if read only mode is enabled and if free disk space is less than 5%
if grep -q read_only_allow_delete "/tmp/escurloutput" && [[ "$DATA_USED_SPACE" -ge 95 ]]; then
        # If both conditions are met, do not block Elasticsearch indexes but send Slack alert instead
        notify_on_slack 2
fi

# Remove temporary curl output file
rm -f /tmp/escurloutput