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

import os
from signal import SIGTERM
from time import monotonic
from typing import Optional

from celery.worker.autoscale import Autoscaler

from apps.task.celery_backend.constants import ENV_VAR_CELERY_SHUTDOWN_WHEN_NO_TASKS_LONGER_THAN_SEC

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


AUTOSCALE_KEEPALIVE = float(os.environ.get('AUTOSCALE_KEEPALIVE', 30))

SHUTDOWN_COOL_DOWN_PERIOD = float(os.environ.get(ENV_VAR_CELERY_SHUTDOWN_WHEN_NO_TASKS_LONGER_THAN_SEC, 30))


class ShutdownWhenNoTasksAutoscaler(Autoscaler):

    def __init__(self,
                 pool,
                 max_concurrency,
                 min_concurrency=0,
                 worker=None,
                 keepalive=AUTOSCALE_KEEPALIVE,
                 mutex=None):
        super().__init__(pool, max_concurrency, min_concurrency, worker, keepalive, mutex)
        self.cool_down_period_sec = SHUTDOWN_COOL_DOWN_PERIOD
        self.no_tasks_start: Optional[float] = None
        print(
            f'Configuring celery to shutdown when there were no tasks for more than f{self.cool_down_period_sec} seconds.')

    def _maybe_scale(self, req=None):
        res = super()._maybe_scale(req)

        if self.qty:
            # if there are tasks then reset "no tasks" time counter
            self.no_tasks_start = None
        elif not self.no_tasks_start:
            # if there are no tasks and the "no tasks" counter is not started - then start it
            self.no_tasks_start = monotonic()
        elif monotonic() - self.no_tasks_start > self.cool_down_period_sec:
            # if there are no tasks and the counter is started and the time out passed - then shutdown
            print(f'Shutting down because there were no tasks for more than {self.cool_down_period_sec} seconds')
            os.kill(os.getpid(), SIGTERM)

        return res
