#!/usr/bin/env bash

# monitor down docker services - cp to syslog - read in Elastalert
EXCLUDED_FROM_TRACKING='contraxsuite_contrax-flower|contraxsuite_contrax-powa-web'

if [ -v CUSTOMER_DOCKER_SERVICES_EXCLUDED_FROM_TRACKING ]; then
    EXCLUDED_FROM_TRACKING="$EXCLUDED_FROM_TRACKING|$CUSTOMER_DOCKER_SERVICES_EXCLUDED_FROM_TRACKING"
fi

DOWN_SERVICES=`sudo docker service ls --format "{{.Name}} (mode: {{.Mode}}, replicas: {{.Replicas}})" | grep " 0/" | grep -Ev "$EXCLUDED_FROM_TRACKING" | sed ':a;N;$!ba;s/\n/; /g'`
DOWN_SERVICES_COUNT=`echo "$DOWN_SERVICES" | grep -o 'replicas' | wc -l`

if [[ ! "$DOWN_SERVICES_COUNT" -eq 0 ]]; then
    logger -t down_docker_services -p syslog.warn "Detected $DOWN_SERVICES_COUNT down docker service(s): $DOWN_SERVICES."
fi
