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

import json
import os

from django.core.management import BaseCommand
from swagger_view import CustomOpenAPISchemaGenerator
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.request import Request

from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):

    def add_arguments(self, parser):
        """
        Store openAPI schema in json file
        ./manage.py get_openapi_schema -u admin -p admin
        or
        ./manage.py get_openapi_schema -u admin -p admin -o schemas -n schema1.json -i=2
        -o (output folder) and -n (file name) are optional, default is ./openapi_schema.json
        """
        super().add_arguments(parser)
        parser.add_argument(
            '-o', '--output_folder', dest='output_folder', action='store', default='.',
            help='Output folder path'
        )
        parser.add_argument(
            '-n', '--file_name', dest='file_name', action='store', default='openapi_schema.json',
            help='Output file name'
        )
        parser.add_argument(
            '-u', '--username', dest='username', action='store',
            help='User username'
        )
        parser.add_argument(
            '-p', '--password', dest='password', action='store',
            help='User password'
        )
        parser.add_argument(
            '-i', '--indent', dest='indent', action='store',
            help='Pretty-printed with that indent level'
        )

    def handle(self, *args, **options):
        request = APIRequestFactory().request()
        try:
            user = User.objects.get(username=options['username'])
            assert user.check_password(options['password']) is True
        except:
            raise PermissionError('Wrong username or password')
        force_authenticate(request, user=user)
        request = Request(request=request)
        schema = CustomOpenAPISchemaGenerator().get_schema(request=request)
        indent = int(options['indent']) if options.get('indent') is not None else None
        schema_str = json.dumps(schema, indent=indent)

        output_file_path = os.path.join(options['output_folder'], options['file_name'])
        with open(output_file_path, 'w') as f:
            f.write(schema_str)

        print(f'OpenAPI schema has been stored in "{output_file_path}", '
              f'content length is {len(schema_str)} bytes')
