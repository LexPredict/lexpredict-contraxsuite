#!/usr/bin/env bash

pushd ../

source volumes.sh
source setenv.sh

export SLACK_WEBHOOK=$1

echo "=== Setting up letsencrypt certs ==="

sudo add-apt-repository ppa:certbot/certbot -y
sudo apt-get update
sudo apt-get install -y certbot

echo "=== Stopping docker service ==="

sudo service docker stop

# Run the following commands if apache2 blocks port 80
# sudo update-rc.d apache2 disable
# sudo service apache2 stop

sudo certbot certonly --standalone --preferred-challenges http -d ${DOCKER_DJANGO_HOST_NAME} --config-dir ./.certs --agree-tos --email "support@lexpredict.com" --non-interactive --deploy-hook "touch certificate_change_occured"
sudo cp ./.certs/live/${DOCKER_DJANGO_HOST_NAME}/fullchain.pem ${VOLUME_NGINX_CERTS}certificate.pem
sudo cp ./.certs/live/${DOCKER_DJANGO_HOST_NAME}/privkey.pem ${VOLUME_NGINX_CERTS}certificate.key
sudo rm -r ./.certs

if [ -e ./certificate_change_occured ]
then
  curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Letsencrypt renewal bot\", \"text\": \"The certificate for ${DOCKER_DJANGO_HOST_NAME} has been successfully renewed.\", \"icon_emoji\": \":ok_hand:\"}" $SLACK_WEBHOOK || echo  "Certificate updated"
else
  curl -X POST --data-urlencode "payload={\"channel\": \"#ops-notifications\", \"username\": \"Letsencrypt renewal bot\", \"text\": \"There was a problem with renewing certificate for ${DOCKER_DJANGO_HOST_NAME}.\", \"icon_emoji\": \":thumbsdown:\"}" $SLACK_WEBHOOK || echo "Certificate not updated"
fi

sudo rm ./certificate_change_occured

echo "=== Starting docker service ==="

sudo service docker start

popd