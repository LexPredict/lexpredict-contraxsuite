#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=settings

pylint ../contraxsuite_services --rcfile=.pylintrc > pylint_result.html