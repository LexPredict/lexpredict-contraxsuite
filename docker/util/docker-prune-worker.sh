#!/bin/sh
set +e

WORKER_PEM=$1
WORKER_IP=$2

echo "Cleaning worker ${WORKER_IP} using PEM file ${WORKER_PEM}..."

ssh -o StrictHostKeyChecking=no -i ${WORKER_PEM} ubuntu@${WORKER_IP} sudo docker system prune -f
echo "Sent docker system prune command to: ${WORKER_IP}."

