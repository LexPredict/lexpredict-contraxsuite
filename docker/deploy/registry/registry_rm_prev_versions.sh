#!/bin/sh

sudo docker pull anoxis/registry-cli
sudo docker run --rm --network=contraxsuite_registry_net anoxis/registry-cli -r http://registry:5001 --delete --num 1
sudo docker exec -ti contraxsuite_registry_registry.1.$(sudo docker service ps -f 'name=contraxsuite_registry_registry.1' contraxsuite_registry_registry -q --no-trunc | head -n1) /bin/registry garbage-collect /etc/docker/registry/config.yml
exit 0
