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

from apps.document.models import DocumentType
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    """
    Example:
        python manage.py create_document_type \
            --code=dummy_document_type_1 \
            --title='Dummy DocumentType 1'
    """
    help: str = 'Add an empty `DocumentType` to the database.'

    def add_arguments(self, parser):
        """
        """
        parser.add_argument(
            '-c', '--code',
            nargs=None,
            type=str,
            required=True,
            help=DocumentType._meta.get_field('code').help_text,
        )

        parser.add_argument(
            '-t', '--title',
            nargs=None,
            type=str,
            required=True,
            help='Titles are less-restrictive friendly names '
                 'and can be duplicated or edited at any time.'
        )

    def handle(self, *args, **options):
        """
        """
        try:
            new_document_type: DocumentType = \
                DocumentType.objects.create(
                    code=options['code'],
                    title=options['title']
                )
            self.stdout.write(
                f'Created new DocumentType: '
                f'[code: {new_document_type.code} '
                f'| title: {new_document_type.title} '
                f'| uid: (#{new_document_type.pk})]'
            )
        except IntegrityError as integrity_error:
            tab: str = '\n -->'
            message: str = f'{tab} '.join(integrity_error.args[0].split("\n")[:-1])
            self.stdout.write(
                f'{"-" * 79}'
                '\nException encountered!'
                f'{tab} {integrity_error.__cause__.__class__.__name__}'
                f'{tab} {message}'
                f'{tab} Unable to create new DocumentType with code: "{options["code"]}".'
                f'\n{"-" * 79}'
            )
