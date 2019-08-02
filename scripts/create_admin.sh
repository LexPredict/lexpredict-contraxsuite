#!/bin/sh
echo To be run within contraxsuite python venv with: source create_admin.sh
pushd ../contraxsuite_services
python manage.py create_superuser --username=Administrator --password=Administrator --email=admin@contraxsuite.local 
popd

