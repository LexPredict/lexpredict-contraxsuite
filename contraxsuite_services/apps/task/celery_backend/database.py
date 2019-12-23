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

from __future__ import absolute_import, unicode_literals

from celery.backends.base import BaseDictBackend

from apps.task.models import Task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DatabaseBackend(BaseDictBackend):
    """The Django database backend, using models to store task state."""

    TaskModel = Task

    subpolling_interval = 0.5

    def _store_result(self, task_id, result, status,
                      traceback=None, request=None):
        """Store return value and status of an executed task."""
        metadata = {
            'children': self.current_task_children(request),
        }

        task_name = None

        if request:
            if hasattr(request, 'name') and request.name:
                task_name = request.name
            elif hasattr(request, 'task') and request.task:
                if hasattr(request.task, 'name') and request.task.name:
                    task_name = request.task.name
                else:
                    task_name = str(request.task)
            else:
                task_name = str(request)

        if not task_name:
            task_name = 'Unrecognized Task'
            print('Was unable to recognize task: task_id={0}\n'
                  'result={1}\n'
                  'status={2}\n'
                  'request={3}'.format(task_id, result, status, request))

        self.TaskModel.objects.store_result(
            task_id,
            request.root_id if request else None,
            task_name,
            result,
            status,
            traceback=traceback,
            metadata=metadata,
        )

        return result

    @staticmethod
    def task_to_decoded(task: TaskModel):
        return {
            'task_id': task.id,
            'name': task.name,
            'status': task.own_status,
            'result': task.result,
            'date_start': task.date_start,
            'traceback': task.traceback,
            'metadata': task.celery_metadata,
        }

    def exception_to_python(self, exc):
        try:
            return super().exception_to_python(exc)
        except KeyError:
            return exc

    def _get_task_meta_for(self, task_id):
        """Get task metadata for a task by id."""
        obj = self.TaskModel.objects.get_task(task_id)
        res = self.task_to_decoded(obj)
        meta = res.get('metadata') or dict()
        res.update(meta,
                   result=res.get('result'))
        return self.meta_from_decoded(res)

    def _forget(self, task_id):
        try:
            self.TaskModel.objects.get(task_id=task_id).delete()
        except self.TaskModel.DoesNotExist:
            pass

    def cleanup(self):
        """Delete expired metadata."""
        self.TaskModel.objects.delete_expired(self.expires)
