#!/usr/bin/env bash

export AWS_ACCESS_KEY_ID=$1
export AWS_SECRET_ACCESS_KEY=$2

set -e
pushd ..
source setenv.sh
popd

apt-get update -qq && apt-get -y -qq install awscli
unset -v latest
for file in "/data/docker/volumes/contraxsuite_backup/_data/db"/*; do
  [[ $file -nt $latest ]] && latest=$file
done
aws s3 cp $latest s3://$3/$DOCKER_DJANGO_HOST_NAME/