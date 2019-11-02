#!/bin/sh

WORKER_PEM=$1

if [ "${WORKER_PEM}" = "" ]; then
	echo "Usage: reboot-workers.sh worker_key.pem"
	exit 1
elif [ ! -f ${WORKER_PEM} ]; then
	echo "PEM file not found: ${WORKER_PEM}"
	exit 1
else
	echo "Removing down Docker Swarm nodes..."
	sudo docker node ls --filter role=worker|grep Down|grep -o '^\S\+'|xargs sudo docker node rm
	echo "Finished removing down nodes."


	echo "Restarting all Docker Swarm Workers using PEM file ${WORKER_PEM}..."

	docker node ls --filter "role=worker" --format "{{.Hostname}}"|grep -v ip-172-31-18-215|xargs -L 1 ./thread_dump_worker.sh ${WORKER_PEM}

	echo "Finished restarting all Docker Swarm workers."
fi

