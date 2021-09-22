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

from apps.project.tasks import CleanProject, CleanProjects
from apps.task.tasks import call_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    """
    call like
    ./manage.py delete_projects -i 101 102
    or
    ./manage.py delete_projects -s=True -i 101 102 104
    for safe but slow deleting
    """

    help = "Load FieldAnnotationStatus objects from fixtures, skip if any exists."
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('-i', '--ids', nargs='+', type=int, required=True,
                            help='Project id list separated by space to be deleted.')
        parser.add_argument('-d', '--delete', nargs='?', type=bool, required=False, default=True,
                            help='Whether a project should be deleted itself.')
        parser.add_argument('-s', '--safe', nargs='?', type=bool, required=False, default=True,
                            help='Disable triggers on tables before deleting rows.')
        parser.add_argument('-a', '--async', nargs='?', type=bool, required=False, default=True,
                            help='Use async celery task VS running it synchronously.')

    def handle(self, *args, **options):

        ids = options.get('ids') or []
        delete_project_itself = options.get('delete')
        safe_delete = options.get('safe')
        do_async = options.get('async')

        if do_async is True:
            call_task(CleanProjects,
                      _project_ids=ids,
                      delete=delete_project_itself,
                      safe_delete=safe_delete)
        else:
            start = datetime.datetime.now()

            for id in ids:
                delete_task = CleanProject()
                delete_task.process(_project_id=id,
                                    delete=delete_project_itself,
                                    safe_delete=safe_delete,
                                    skip_task_updating=True)

            time_elapsed = (datetime.datetime.now() - start).total_seconds()
            self.stdout.write(f'Deleting {len(ids)} project(s) took {time_elapsed} s.')
