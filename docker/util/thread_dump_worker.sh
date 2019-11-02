#!/bin/sh
set +e

WORKER_PEM=$1
WORKER_IP=$2

echo "Restarting worker ${WORKER_IP} using PEM file ${WORKER_PEM}..."

ssh -o StrictHostKeyChecking=no -i ${WORKER_PEM} ubuntu@${WORKER_IP} sudo pkill -f celery --signal 39
echo "Sent restart command to: ${WORKER_IP}."

