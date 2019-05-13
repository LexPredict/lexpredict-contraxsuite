#!/bin/bash

source hash_sums.sh

pushd ../../..

mkdir -p ./config-templates-dst

copy_unchanged_files contraxsuite_services/apps/notifications/notification_templates \
    contraxsuite_services/media/data/notification_templates \
    contraxsuite_services/media/data/notification_templates_hashes

popd