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

from celery import shared_task
from django.conf import settings

import task_names
# Project imports
from apps.materialized_views.mat_views import MaterializedViews
from apps.task.tasks import CeleryTaskLogger, ExtendedTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@shared_task(base=ExtendedTask, name=task_names.TASK_NAME_REFRESH_MATERIALIZED_VIEW, bind=True)
def refresh_materialized_view(_celery_task, view_name: str):
    mat_views_repo = MaterializedViews()
    mat_views_repo.refresh_materialized_view(CeleryTaskLogger(_celery_task), view_name)


@shared_task(base=ExtendedTask, name=task_names.TASK_NAME_PLAN_REFRESHING_MATERIALIZED_VIEWS, bind=True,
             queue=settings.CELERY_QUEUE_SERIAL)
def plan_refreshing_materialized_views(_celery_task):
    mat_views_repo = MaterializedViews()

    def refresh_view(view_name: str):
        refresh_materialized_view.apply_async((view_name,))

    mat_views_repo.plan_refreshes(CeleryTaskLogger(_celery_task),
                                  task_names.TASK_NAME_REFRESH_MATERIALIZED_VIEW,
                                  refresh_view)
