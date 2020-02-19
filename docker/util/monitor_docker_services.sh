#!/usr/bin/env bash

EXCLUDED_FROM_TRACKING='contraxsuite_contrax-flower|contraxsuite_contrax-powa-web'

DOWN_SERVICES=`sudo docker service ls --format "Service: {{.Name}}, Mode: {{.Mode}}, Replicas: {{.Replicas}};\n"|grep " 0/"|grep -Ev "$EXCLUDED_FROM_TRACKING"`
DOWN_SERVICES_COUNT=`echo "$DOWN_SERVICES" | grep '[^ ]' | wc -l`

if [[ ! "$DOWN_SERVICES_COUNT" -eq 0 ]]; then
    echo {\"down_services\": \"$DOWN_SERVICES\", \"down_services_count\": $DOWN_SERVICES_COUNT, \"timestamp\": \"`date +'%Y-%m-%d %T'`\"}
fi
