#!/usr/bin/env bash

crontab -l > crontemp && cat crontemp | grep "bash update-nginx-certificates-no-input.sh" >/dev/null || echo "0 0 * * 7 cd /data/deploy/contraxsuite-deploy/docker/util && sudo bash update-nginx-certificates-no-input.sh > /dev/null 2>&1" >> crontemp && cat crontemp | crontab - && rm crontemp
