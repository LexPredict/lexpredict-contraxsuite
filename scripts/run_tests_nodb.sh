#!/bin/bash

set -e
echo To be run within contraxsuite python venv
pushd ../contraxsuite_services

python manage.py test --settings=nodb_settings

popd

