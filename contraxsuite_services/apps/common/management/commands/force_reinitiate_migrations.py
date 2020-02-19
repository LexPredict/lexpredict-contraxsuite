"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

# Imports
import os
import shutil

from django.core.management.commands.migrate import Command as MigrateCommand
from django.conf import settings
from django.core.management import call_command
from django.db import connection

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(MigrateCommand):
    help = "Remove all migrations, re-create them from scratch, " \
           "Drop django_migrations table and re-fill that table with new-created migrations"
    requires_system_checks = False

    def handle(self, *args, **options):

        # 1. remove migration files
        custom_apps = [i.replace('apps.', '') for i in settings.INSTALLED_APPS if
                       i.startswith('apps.')]
        for app_name in custom_apps:
            app_migrations_path = os.path.join(settings.PROJECT_DIR, f'apps/{app_name}/migrations')
            shutil.rmtree(app_migrations_path, ignore_errors=True)

        # drop migrations table
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE django_migrations;')

        # re-create migration files
        call_command('makemigrations', 'common')
        call_command('makemigrations')

        # re-fill migrations
        call_command('migrate', '--fake')
