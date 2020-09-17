#!/bin/bash

pushd ..
source setenv.sh
source volumes.sh
popd

mkdir ./temp

# Running openssl as root does not work because of some rnd generator issues on some environments
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./temp/certificate.key -out ./temp/certificate.pem

sudo mv ./temp/certificate.key ${VOLUME_NGINX_CERTS}
sudo mv ./temp/certificate.pem ${VOLUME_NGINX_CERTS}
sudo chown root:root ${VOLUME_NGINX_CERTS}certificate.key
sudo chown root:root ${VOLUME_NGINX_CERTS}certificate.pem
