#!/bin/bash
OUTPUT=$(docker exec -it `docker ps -q --filter name=rabbitmq` rabbitmqctl list_queues -p contrax1_vhost name arguments)
prio_high=$(echo ${OUTPUT} | grep -oP '(?<=high_priority\s\[{"x-max-priority",)\d+')
prio_default=$(echo ${OUTPUT} | grep -oP '(?<=serial\s\[{"x-max-priority",)\d+')
prio_serial=$(echo ${OUTPUT} | grep -oP '(?<=default\s\[{"x-max-priority",)\d+')

echo "High priority queue priority: ${prio_high}"
echo "Default queue priority: ${prio_default}"
echo "Serial queue priority: ${prio_serial}"

if [ "$prio_high" != "10" ] || [ "$prio_default" != "10" ] || [ "$prio_serial" != "10" ]
then
  echo "Queues should be destroyed and recreated"
  docker exec -i `docker ps -q --filter name=rabbitmq` rabbitmqctl stop_app
  docker exec -i `docker ps -q --filter name=rabbitmq` rabbitmqctl reset
  docker exec -i `docker ps -q --filter name=rabbitmq` rabbitmqctl start_app
  echo "Queues are updated"
else
  echo "Queues are actual"
fi
