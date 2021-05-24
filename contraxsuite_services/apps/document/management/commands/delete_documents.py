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

import datetime
from django.core.management import BaseCommand

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    """
    call like
    ./manage.py delete_documents -i 101 102
    or
    ./manage.py delete_documents -s=True -i 101 102 104
    for safe but slow deleting
    """

    help = "Load FieldAnnotationStatus objects from fixtures, skip if any exists."
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('-i', '--ids', nargs='+', type=int, required=True)
        parser.add_argument('-s', '--safe', nargs='?', type=bool, required=False, default=False)

    def handle(self, *args, **options):
        def log_error(message, exc_info: Exception = None, **kwargs):
            if exc_info:
                print(message + '. Exception:\n' + str(exc_info))
            else:
                print(message)
        ids = options.get('ids') or []
        safe_mode = options.get('safe') or False
        from apps.document.tasks import DeleteDocuments
        start = datetime.datetime.now()
        delete_task = DeleteDocuments()
        delete_task.process(_document_ids=ids, _safe_mode=safe_mode, log_error=log_error)
        time_elapsed = (datetime.datetime.now() - start).total_seconds()
        self.stdout.write(f'Deleting {len(ids)} document(s) took {time_elapsed} s.')
