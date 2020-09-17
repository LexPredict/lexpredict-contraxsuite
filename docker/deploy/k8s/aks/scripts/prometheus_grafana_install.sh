#!/bin/bash

pushd ../ > /dev/null
source aks_setenv.sh
popd > /dev/null

set +e

echo "Adding namespace for Prometheus..."
kubectl create namespace ${PROMETHEUS_NAMESPACE}

echo "Installing Nginx Ingress..."
helm install stable/nginx-ingress --namespace ${PROMETHEUS_NAMESPACE} --name ${PROMETHEUS_NGINX_HELM_RELEASE_NAME}

echo "Sleeping to let nginx finish..."

sleep 60

NGINX_EXTERNAL_IP=$(kubectl get services --namespace ${PROMETHEUS_NAMESPACE} ${PROMETHEUS_NGINX_HELM_RELEASE_NAME}-nginx-ingress-controller --output jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ "${GRAFANA_ADD_CLOUDFLARE_DNS,,}" = "yes" ]; then
    source prometheus_grafana_del_dns_records.sh
    echo "Adding DNS entry for domain name ${GRAFANA_DOMAIN_NAME} to lead to ${NGINX_EXTERNAL_IP}"

    curl -X POST "${CLOUDFLARE_DNS_URL}" \
	 -H "Authorization: ${CLOUDFLARE_DNS_AUTHORIZATION}" \
         -H "Content-Type: application/json" \
         --data "{\"type\":\"A\",\"name\":\"${GRAFANA_DOMAIN_NAME}\",\"content\":\"${NGINX_EXTERNAL_IP}\",\"ttl\":1,\"priority\":10,\"proxied\":false}"
    echo ""
    echo "Sleeping some time to let the DNS things finish updating..."
    sleep 30

else
    echo "Prometheus/Graphana will be at the following ip address: ${NGINX_EXTERNAL_IP}"
    echo "Don't forget to add a DNS record for ${GRAFANA_DOMAIN_NAME} to direct to this ip."
fi

if [ "${GRAFANA_ADD_LETSENCRYPT_CERT,,}" = "yes" ]; then

    echo "Adding letsecrypt certificate for ${GRAFANA_DOMAIN_NAME}..."

    mkdir -p ./temp
    envsubst < prometheuscert.template.yml > ./temp/prometheuscert.template
    kubectl apply -f ./temp/prometheuscert.template --namespace ${PROMETHEUS_NAMESPACE}
    echo "Sleeping some time..."
    sleep 30
    kubectl get certificate ${GRAFANA_DOMAIN_NAME}-crt -n ${PROMETHEUS_NAMESPACE}
else
    echo "Skipped adding letsencrypt certificate for ${GRAFANA_DOMAIN_NAME}"
fi

echo "Installing prometheus..."
helm install --name=prometheus stable/prometheus --namespace ${PROMETHEUS_NAMESPACE} --set rbac.create=true

echo "Installing grafana..."
helm install --name grafana stable/grafana --namespace ${PROMETHEUS_NAMESPACE} --set persistence.enabled=true --set persistence.size=8Gi --set ingress.enabled=true --set ingress.hosts[0]=${GRAFANA_DOMAIN_NAME} --set ingress.tls[0].secretName=${GRAFANA_DOMAIN_NAME}-crt --set ingress.tls[0].hosts[0]=${GRAFANA_DOMAIN_NAME} --set rbac.create=true

echo "Retrieving grafana admin password..."
kubectl get secret --namespace prometheus grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
