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

from django.core.management import BaseCommand

from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    help = "Create or Update App Var."

    def add_arguments(self, parser):
        parser.add_argument('--name',
                            help='Name')

        parser.add_argument('--value',
                            help='Value')

        parser.add_argument('--category',
                            help='Category')

        parser.add_argument('--description',
                            help='Description')

    def handle(self, *args, **options):
        app_var, created = AppVar.objects.update_or_create(
            name=options['name'],
            category=options['category'] or 'Common',
            defaults=dict(
                value=options['value'])
        )
        description = options['description']
        if description:
            app_var.description = description
            app_var.save()

        print('AppVar "{}" is {}'.format(app_var.name, 'created' if created else 'updated'))
