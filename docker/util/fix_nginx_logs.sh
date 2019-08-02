#!/bin/bash

if [[ -L "$VOLUME_INTERNAL_NGINX_LOGS/access.log" || -L "$VOLUME_INTERNAL_NGINX_LOGS/error.log" ]]
then
	sudo rm $VOLUME_INTERNAL_NGINX_LOGS/access.log
	sudo rm $VOLUME_INTERNAL_NGINX_LOGS/error.log
	sudo touch $VOLUME_INTERNAL_NGINX_LOGS/access.log
	sudo touch $VOLUME_INTERNAL_NGINX_LOGS/error.log
	sudo chown www-data:adm $VOLUME_INTERNAL_NGINX_LOGS/access.log
	sudo chown www-data:adm $VOLUME_INTERNAL_NGINX_LOGS/error.log
	sudo chmod 640 $VOLUME_INTERNAL_NGINX_LOGS/access.log
	sudo chmod 640 $VOLUME_INTERNAL_NGINX_LOGS/error.log
	sudo docker service scale contraxsuite_contrax-nginx=0
	sudo docker service scale contraxsuite_contrax-nginx=1
fi
