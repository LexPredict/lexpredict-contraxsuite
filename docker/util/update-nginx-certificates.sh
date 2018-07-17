#!/usr/bin/env bash

pushd ../

source volumes.sh

echo -n "Enter your domain name:"
read FQDN

echo "=== Setting up letsencrypt certs ==="

sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot

echo "=== Stopping docker service ==="

sudo service docker stop

sudo certbot certonly --standalone --preferred-challenges http -d ${FQDN} --config-dir ./.certs
sudo cat ./.certs/live/${FQDN}/fullchain.pem > ${VOLUME_NGINX_CERTS}/certificate.pem
sudo cat ./.certs/live/${FQDN}/privkey.pem > ${VOLUME_NGINX_CERTS}/certificate.key
sudo rm -r ./.certs

echo "=== Starting docker service ==="

sudo service docker start

popd
