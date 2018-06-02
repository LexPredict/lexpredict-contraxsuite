#!/bin/sh

sudo docker pull anoxis/registry-cli
sudo docker run --rm --network=contraxsuite_registry_net anoxis/registry-cli -r http://registry:5001
