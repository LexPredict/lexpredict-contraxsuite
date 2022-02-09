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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
from typing import Tuple
from django.db import connection
from apps.task.models import Task
from django.test import TestCase
from django.conf import settings


class TestCalcTaskStatus(TestCase):
    def test_calc_wo_children(self):
        if not settings.ENABLE_LOCAL_TESTS:
            return
        self.create_parent_task('11111111-1111-1111-1111-111111111111')
        status, progress = self.get_task_status_progress('11111111-1111-1111-1111-111111111111')
        self.assertEqual('SUCCESS', status)
        self.assertEqual(100.0, progress)

    def test_calc_failed_child(self):
        if not settings.ENABLE_LOCAL_TESTS:
            return
        self.create_parent_task('11111111-1111-1111-1111-111111111111')
        self.create_failed_child_task('21111111-1111-1111-1111-111111111112',
                                      '11111111-1111-1111-1111-111111111111')
        status, progress = self.get_task_status_progress('11111111-1111-1111-1111-111111111111')
        self.assertEqual('FAILURE', status)
        self.assertEqual(100.0, progress)

    def test_calc_failed_and_on_success_child(self):
        if not settings.ENABLE_LOCAL_TESTS:
            return
        self.create_parent_task('11111111-1111-1111-1111-111111111111')
        self.create_failed_child_task('32222222-1111-1111-1111-111111111113',
                                      '11111111-1111-1111-1111-111111111111')
        self.create_on_success_child_task('42222222-1111-1111-1111-111111111114',
                                          '11111111-1111-1111-1111-111111111111')

        status, progress = self.get_task_status_progress('11111111-1111-1111-1111-111111111111')
        self.assertEqual('FAILURE', status)
        self.assertEqual(100.0, progress)

    def test_calc_on_success_child(self):
        if not settings.ENABLE_LOCAL_TESTS:
            return
        self.create_parent_task('11111111-1111-1111-1111-111111111111')
        self.create_on_success_child_task('42222222-1111-1111-1111-111111111114',
                                          '11111111-1111-1111-1111-111111111111')

        status, progress = self.get_task_status_progress('11111111-1111-1111-1111-111111111111')
        self.assertEqual('PENDING', status)
        self.assertEqual(50.0, progress)

    def get_task_status_progress(self, task_id: str) -> Tuple[str, float]:
        with connection.cursor() as cursor:
            cursor.execute(f'''
                    select t1.id, task_status_to_str(t1.calc_status) as calc_status, 
               round(fix_task_progress_with_status(t1.calc_progress, t1.calc_status)) as calc_progress
        from (select t2.id as id,
                     calc_task_status(t2.id, t2.own_status, t2.has_sub_tasks) as calc_status, 
                     calc_task_progress(t2.id, t2.own_progress, t2.own_status, t2.has_sub_tasks) as calc_progress
                from task_task t2
                where t2.own_status = 'REVOKED' or (t2.worker is not null and 
                    (t2.status is null or t2.status in ('PENDING', 'RETRY', 'REJECTED', 'RECEIVED', 'STARTED')))
             ) as t1
        where t1.id = '{task_id}';            
                    ''')
            for _, status, progress in cursor.fetchall():
                return status, progress

    def create_parent_task(self, id: str):
        task_dad = Task()
        task_dad.name = 'dad'
        task_dad.worker = 'master'
        task_dad.id = id
        task_dad.has_sub_tasks = True
        task_dad.own_status = 'SUCCESS'
        task_dad.own_progress = 100
        task_dad.status = 'PENDING'
        task_dad.progress = 67
        task_dad.save()

    def create_failed_child_task(self, id: str, parent_id: str):
        task_child = Task()
        task_child.name = 'child_failed'
        task_child.worker = 'master'
        task_child.id = id
        task_child.has_sub_tasks = False
        task_child.own_status = 'FAILURE'
        task_child.status = 'FAILURE'
        task_child.own_progress = 100
        task_child.progress = 100
        task_child.propagate_exceptions = False
        task_child.completed = False
        task_child.failure_processed = False
        task_child.run_after_sub_tasks_finished = False
        task_child.parent_task_id = parent_id
        task_child.main_task_id = parent_id
        task_child.save()

    def create_on_success_child_task(self, id: str, parent_id: str):
        task_child = Task()
        task_child.name = 'child_on_success'
        task_child.worker = 'master'
        task_child.id = id
        task_child.has_sub_tasks = False
        task_child.own_status = None
        task_child.status = None
        task_child.own_progress = 0
        task_child.progress = 0
        task_child.propagate_exceptions = False
        task_child.completed = False
        task_child.failure_processed = False
        task_child.run_after_sub_tasks_finished = True
        task_child.parent_task_id = parent_id
        task_child.main_task_id = parent_id
        task_child.save()
