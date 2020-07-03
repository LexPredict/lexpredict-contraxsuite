#!/bin/bash

pushd ../contraxsuite_services
uwsgi --plugins python3 --wsgi wsgi:application --buffer-size 65535 --protocol http --socket 0.0.0.0:8000 --stats /tmp/stats.socket
popd
