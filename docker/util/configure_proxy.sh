#!/bin/bash

pushd ../
source setenv.sh
popd

if [[ -z "${PROXY_SERVER_HTTP}" ]]; then
    echo "Http proxy server is not configured in setenv.sh"
else
    grep -q -F "http_proxy=\"${PROXY_SERVER_HTTP}\"" /etc/environment || echo "http_proxy=\"${PROXY_SERVER_HTTP}\"" | tee --append /etc/environment
    grep -q -F 'no_proxy="localhost,127.0.0.1"' /etc/environment || echo 'no_proxy="localhost,127.0.0.1"' | tee --append /etc/environment
    grep -q -F "Environment=\"HTTP_PROXY=${PROXY_SERVER_HTTP}\"" /lib/systemd/system/docker.service || sed -i "/^\[Service\]/a Environment=\"HTTP_PROXY=${PROXY_SERVER_HTTP}\"" /lib/systemd/system/docker.service
    grep -q -F "Environment=\"NO_PROXY=localhost,127.0.0.1\"" /lib/systemd/system/docker.service || sed -i "/^\[Service\]/a Environment=\"NO_PROXY=localhost,127.0.0.1\"" /lib/systemd/system/docker.service
fi


if [[ -z "${PROXY_SERVER_HTTPS}" ]]; then
    echo "Https proxy server is not configured in setenv.sh"
else
    grep -q -F "https_proxy=\"${PROXY_SERVER_HTTPS}\"" /etc/environment || echo "https_proxy=\"${PROXY_SERVER_HTTPS}\"" | tee --append /etc/environment
    grep -q -F "Environment=\"HTTPS_PROXY=${PROXY_SERVER_HTTPS}\"" /lib/systemd/system/docker.service || sed -i "/^\[Service\]/a Environment=\"HTTPS_PROXY=${PROXY_SERVER_HTTPS}\"" /lib/systemd/system/docker.service

fi
