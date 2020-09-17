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

# Future imports
from __future__ import absolute_import

# Standard imports
import os

# Celery imports
import django
from celery import signals
from celery.app import trace
from celery.signals import task_failure
from django.db import InterfaceError

# Project imports
from apps import celery_worker_roles

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Set celery environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # pragma: no cover

WAS_INIT = False
try:
    django.setup()
except RuntimeError:
    WAS_INIT = True

if True:  # not WAS_INIT:

    # advanced_celery adds workarounds for celery issue which requires specific import order
    from apps.task.celery_backend.advanced_celery import AdvancedCelery  # noqa
    from apps.task.utils.task_utils import TaskUtils

    def on_failure(*args, **kwargs):
        exc = kwargs.get('exception')
        if not exc:
            return
        if isinstance(exc, InterfaceError):
            if exc.args and 'connection already closed' in exc.args[0]:
                print('on_failure(InterfaceError): shutting down DB connection')
                # clear the DB connection
                TaskUtils.prepare_task_execution()

    task_failure.connect(on_failure)

    app = AdvancedCelery('apps')

    def add_preload_options(parser):
        parser.add_argument(
            '-R', '--role', default=None,
            help='Celery worker role.',
        )

    app.user_options['preload'].add(add_preload_options)

    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks(force=True)
    app.conf.task_default_priority = 5

    old_build_tracer = trace.build_tracer

    def build_tracer_patched(name, task, loader=None, hostname=None, *args, **kwargs):
        old_trace_task = old_build_tracer(name, task, loader, hostname, *args, **kwargs)
        worker = hostname

        def trace_task_patched(uuid, *args1, **kwargs1):
            from apps.task.utils.task_utils import TaskUtils
            from apps.task.models import Task

            TaskUtils.prepare_task_execution()
            Task.objects.start_processing(task_id=uuid, worker=worker)

            return old_trace_task(uuid, *args1, **kwargs1)

        return trace_task_patched

    trace.build_tracer = build_tracer_patched

    @app.task(bind=True)
    def debug_task(self):
        print('Request: {0!r}'.format(self.request))  # pragma: no cover

    @signals.user_preload_options.connect
    def on_preload_parsed(options, **kwargs):
        app.user_options[celery_worker_roles.WORKER_ROLE] = options.get(celery_worker_roles.WORKER_ROLE)
