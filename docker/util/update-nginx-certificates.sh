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

# To not block port 80
sudo update-rc.d apache2 disable
sudo service apache2 stop

sudo certbot certonly --standalone --preferred-challenges http -d ${FQDN} --config-dir ./.certs
sudo cp ./.certs/live/${FQDN}/fullchain.pem ${VOLUME_NGINX_CERTS}certificate.pem
sudo cp ./.certs/live/${FQDN}/privkey.pem ${VOLUME_NGINX_CERTS}certificate.key
sudo rm -r ./.certs

echo "=== Starting docker service ==="

sudo service docker start

popd
