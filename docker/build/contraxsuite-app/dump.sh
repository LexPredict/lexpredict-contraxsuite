#!/bin/bash

cd /contraxsuite_services
source venv/bin/activate

python manage.py dump_data --dst-file=fixtures/additional/app-dump.json
