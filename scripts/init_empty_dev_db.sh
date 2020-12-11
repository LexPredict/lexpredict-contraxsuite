#!/bin/bash
set -e
echo To be run within contraxsuite python venv with: source init_empty_dev_dv.sh
pushd ../contraxsuite_services

python manage.py migrate
python manage.py create_superuser --username=Administrator --password=Administrator --email=admin@contraxsuite.local
popd

