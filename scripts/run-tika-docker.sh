#!/bin/sh

sudo docker pull logicalspark/docker-tikaserver

sudo docker run -p 9998:9998 logicalspark/docker-tikaserver
