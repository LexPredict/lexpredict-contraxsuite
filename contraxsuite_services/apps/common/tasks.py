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

from django.conf import settings
from django.db import connection

# Project imports
import task_names
from apps.celery import app
from apps.common.models import MethodStats, MethodStatsCollectorPlugin
from apps.common.decorators import collect_stats, decorate
from apps.task.tasks import BaseTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@app.task(name=task_names.TASK_NAME_DELETE_METHOD_STATS, bind=True)
def delete_method_stats(_celery_task):
    """
    Delete all MethodStats objects
    """
    MethodStats.objects.all().delete()


@app.task(name=task_names.TASK_NAME_INIT_METHOD_STATS_COLLECTORS, bind=True)
def init_method_stats_collectors(_celery_task):
    """
    Initiate collect_stats decorators on system start
    """
    for instance_values in MethodStatsCollectorPlugin.objects.values():
        decorate(collect_stats, **instance_values)


class ReindexDB(BaseTask):
    """
    Reindex DB and run VACUUM ANALYZE
    """
    name = 'Reindex DB'
    priority = 9

    def process(self, **kwargs):
        do_reindex = kwargs.get('reindex')
        do_vacuum = kwargs.get('vacuum')

        if do_reindex:
            with connection.cursor() as cursor:
                cursor.execute('REINDEX DATABASE {};'.format(settings.DATABASES['default']['NAME']))

        if do_vacuum:
            with connection.cursor() as cursor:
                cursor.execute('VACUUM ANALYZE;')


app.register_task(ReindexDB())
