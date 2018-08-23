#!/usr/bin/env bash

sudo docker node ls --filter role=worker|grep Down|grep -o '^\S\+'|xargs sudo docker node rm

