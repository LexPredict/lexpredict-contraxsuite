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
from django.db import transaction
from django.db.models import F

from apps.common.utils import fast_uuid  # noqa
from apps.task.models import Task  # noqa
from apps.task.utils.task_utils import TaskUtils  # noqa

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AdvancedCelery(Celery):

    def re_send_task(self, task_id: str):
        """
        Re-send a task into the broker by task_id.
        Uses args, kwargs and other info about the task from the DB - see send_task() method below which stores them.
        """
        task_name, task_args, task_kwargs, task_queue, task_priority \
            = Task.objects.filter(pk=task_id).values_list('name', 'args', 'kwargs', 'queue', 'priority')[0]
        amqp = self.amqp
        message = amqp.create_task_message(
            task_id=task_id,
            name=task_name,
            args=task_args,
            kwargs=task_kwargs,
            countdown=None,  # we don't need countdown when re-sending, it was already delayed before hanging
            eta=None,
            group_id=None,
            expires=None,
            retries=0,
            chord=None,  # we have own implementation of chords
            callbacks=None,
            errbacks=None,
            reply_to=None,
            time_limit=None,
            soft_time_limit=None,  # do we need this or this limit is read from the task class/func on the consumer side
            create_sent_event=False,
            root_id=None,
            parent_id=None,
            shadow=None,
            chain=None,
            now=None,
            timezone=None,
            origin=None,
            argsrepr=None,
            kwargsrepr=None
        )
        with self.producer_or_acquire(producer=None) as P:
            with P.connection._reraise_as_library_errors():
                amqp.send_task_message(P, task_name, message, queue=task_queue, priority=task_priority)
        Task.objects.filter(pk=task_id).update(restart_count=F('restart_count') + 1)
        return self.AsyncResult(task_id)

    def send_task(self, name, args=None, kwargs=None, countdown=None, eta=None, task_id=None,
                  producer=None, connection=None, router=None, result_cls=None, expires=None,
                  publisher=None, link=None, link_error=None, add_to_parent=True, group_id=None,
                  retries=0, chord=None, reply_to=None, time_limit=None, soft_time_limit=None,
                  root_id=None, parent_id=None, source_data=None,
                  run_after_sub_tasks_finished=False,
                  run_if_parent_task_failed=False,
                  route_name=None, shadow=None, chain=None, task_type=None, main_task_id=None,
                  **options):
        """
        Custom Celery send_task() method which stores a lot of additional required info in the DB.
        There is a task re-sending method in this class which is used to re-start hanged tasks
        lost by workers because of unexpected too fast restart or any other similar reason.
        Task re-send feature requires all the required task info to be stored in the DB
        because the info in the RabbitMQ usually appears lost in case the worker has lost the task.

        Take into account that args, kwargs, queue, priority are required to save in the DB in the same
        form as can be used for loading and re-sending.
        """
        task_id = task_id or str(fast_uuid())

        main_task_id = main_task_id or parent_id or root_id
        args_str = ', '.join([str(arg) for arg in args]) if args else ''
        kwargs_str = '\n'.join([f'{f}: {str(v)}' for f, v in kwargs.items()]) if kwargs else ''

        description = []
        if args_str:
            description.append(args_str)

        if kwargs_str:
            description.append(kwargs_str)

        TaskUtils.prepare_task_execution()
        with transaction.atomic():
            # it is important to save args, kwargs, queue, priority and other task fields
            # because they can be used for the task re-sending
            Task.objects.init_task(task_id=task_id,
                                   task_name=name,
                                   main_task_id=main_task_id,
                                   parent_task_id=parent_id,
                                   description='\n'.join(description),
                                   args=args,
                                   kwargs=kwargs,
                                   queue=options.get('queue'),
                                   priority=options.get('priority'),
                                   source_data=source_data,
                                   run_after_sub_tasks_finished=run_after_sub_tasks_finished,
                                   run_if_parent_task_failed=run_if_parent_task_failed)
            if parent_id is not None:
                Task.objects.filter(id=parent_id).exclude(has_sub_tasks=True).update(has_sub_tasks=True)

        return super().send_task(name, args, kwargs, countdown, eta, task_id, producer, connection,
                                 router, result_cls, expires, publisher, link, link_error,
                                 add_to_parent, group_id, retries, chord, reply_to, time_limit,
                                 soft_time_limit, root_id, parent_id, route_name, shadow, chain,
                                 task_type, **options)
