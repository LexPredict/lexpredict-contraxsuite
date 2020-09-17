#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

echo "Deleting DNS records for domain ${GRAFANA_DOMAIN_NAME}..."
curl -X GET "${CLOUDFLARE_DNS_URL}" \
     -H "Authorization: ${CLOUDFLARE_DNS_AUTHORIZATION}" \
     -H "Content-Type: application/json"  | jq -r ".result[] | select(.name == \"${GRAFANA_DOMAIN_NAME}\") | .id" | while read -r DNS_RECORD_ID ; do

    echo "Deleting: ${DNS_RECORD_ID}"
    curl -X DELETE "${CLOUDFLARE_DNS_URL}/${DNS_RECORD_ID}" \
         -H "Authorization: ${CLOUDFLARE_DNS_AUTHORIZATION}"
done


