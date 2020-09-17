#!/bin/sh

WORKER_PEM=$1

if [ "${WORKER_PEM}" = "" ]; then
	echo "Usage: docker-prune-workers.sh worker_key.pem"
	exit 1
elif [ ! -f ${WORKER_PEM} ]; then
	echo "PEM file not found: ${WORKER_PEM}"
	exit 1
else
	echo "Removing down Docker Swarm nodes..."
	sudo docker node ls --filter role=worker|grep Down|grep -o '^\S\+'|xargs sudo docker node rm
	echo "Finished removing down nodes."


	echo "Pruning all Docker Swarm Workers using PEM file ${WORKER_PEM}..."

	docker node ls --filter "role=worker" --format "{{.Hostname}}"|xargs -L 1 ./docker-prune-worker.sh ${WORKER_PEM}

	echo "Finished cleaning all Docker Swarm workers."
fi

