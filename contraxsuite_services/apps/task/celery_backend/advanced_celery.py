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

from celery import Celery  # noqa

from apps.common.utils import fast_uuid  # noqa
from apps.task.models import Task  # noqa
from apps.task.utils.task_utils import TaskUtils  # noqa

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AdvancedCelery(Celery):
    def send_task(self, name, args=None, kwargs=None, countdown=None, eta=None, task_id=None,
                  producer=None, connection=None, router=None, result_cls=None, expires=None,
                  publisher=None, link=None, link_error=None, add_to_parent=True, group_id=None,
                  retries=0, chord=None, reply_to=None, time_limit=None, soft_time_limit=None,
                  root_id=None, parent_id=None, source_data=None, run_after_sub_tasks_finished=False,
                  route_name=None, shadow=None, chain=None, task_type=None, main_task_id=None,
                  **options):
        task_id = task_id or str(fast_uuid())

        TaskUtils.prepare_task_execution()

        main_task_id = main_task_id or parent_id or root_id
        args_str = ', '.join([str(arg) for arg in args]) if args else ''
        kwargs_str = ', '.join([f'{f}={str(v)}' for f, v in kwargs.items()]) if kwargs else ''

        Task.objects.init_task(task_id, name, main_task_id,
                               f'Args: {args_str}\nKwargs: {kwargs_str}',
                               args, source_data, run_after_sub_tasks_finished)  # type: Task

        return super().send_task(name, args, kwargs, countdown, eta, task_id, producer, connection,
                                 router, result_cls, expires, publisher, link, link_error,
                                 add_to_parent, group_id, retries, chord, reply_to, time_limit,
                                 soft_time_limit, root_id, parent_id, route_name, shadow, chain,
                                 task_type, **options)
