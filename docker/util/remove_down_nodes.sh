#!/usr/bin/env bash

export DOWN_NODES_NUM=$(sudo docker node ls --filter role=worker|grep Down|grep -o '^\S\+'|wc -l)
if [ "${DOWN_NODES_NUM}" -gt 0 ]; then
  sudo docker node ls --filter role=worker|grep Down|grep -o '^\S\+'|xargs sudo docker node rm;
fi
