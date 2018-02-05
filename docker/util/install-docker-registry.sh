#!/bin/bash

sudo docker service create --name registry-test --publish=5001:5001 \
 --constraint=node.role==manager \
 -e REGISTRY_HTTP_ADDR=0.0.0.0:5001 \
 registry:latest