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

from datetime import datetime, timedelta
from typing import Callable, Type

from celery.states import PENDING
from django.db import connection, transaction, models
from django.utils import timezone

from apps.common.log_utils import ProcessLogger
from apps.common.singleton import Singleton
from apps.common.sql_commons import SQLClause, fetch_bool
from apps.materialized_views.models import MaterializedView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


TABLE_M_VIEW = 'materialized_views_materializedview'
TABLE_M_VIEW_REQUEST = 'materialized_views_materializedviewrefreshrequest'


@Singleton
class MaterializedViews:
    # Worker refresh proc (args: refresh request date):
    # 1. Get advisory lock on the number of the refreshed view (there should be a dict [ view name -> int ] in the code.
    # 2. If already locked by somebody else then quit otherwise continue.
    # 3. Refresh the view.
    # 4. Delete requests with requested_at <= specified request date.
    # 5. Unlock.
    #
    # Celery beat: every minute:
    # 1. Select table_name, max(requested_at).
    # 2. For each existing record try to acquire the advisory lock on the number of the table.
    # 3. If locked by somebody else - continue to the next table.
    # 4. If successfully acquired the lock - unlock it and plan the refresh proc.

    def advisory_lock_by_relation_name(self, cursor, rel_name: str):
        """
        Try acquiring a PG advisory lock by an integer identifier matching the specified relation name and exit
        immediately.
        This is equal locking by table name until the transaction ends.
        :param cursor:
        :param rel_name:
        :return:
        """
        sql = SQLClause('''select pg_try_advisory_xact_lock(
                                        (select c.oid id from pg_class c where c.relname = %s limit 1)::integer
                                                           )''', [rel_name])
        return fetch_bool(cursor, sql)

    def refresh_materialized_view(self, log: ProcessLogger, view_name: str):
        """
        Refresh the specified materialized view and delete all refresh requests older or equal to the last request date
        taken at this method start.

        Additionally this method acquires a PG advisory lock to prevent
        parallel refreshing of the same view.
        The lock is used by the planning routine which tries to acquire the lock
        to prevent re-planning the same refresh if it is already running.
        :param view_name:
        :param log
        :return:
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'update {TABLE_M_VIEW} '
                               'set status=%s where view_name=%s;',
                               [MaterializedView.VIEW_STATUS_UPDATING, view_name])
        except Exception as e:
            log.error(f'Error saving updated status for view "{view_name}": {e}')

        with transaction.atomic():
            with connection.cursor() as cursor:
                if not self.advisory_lock_by_relation_name(cursor, view_name):
                    log.info(f'Canceled refreshing materialized view: {view_name}. '
                             f'Unable to acquire the advisory lock.')
                    cursor.execute(f'update {TABLE_M_VIEW} '
                                   'set status=%s where view_name=%s;',
                                   [MaterializedView.VIEW_STATUS_UPDATED, view_name])
                    return
                log.info(f'Refreshing materialized view: {view_name}.')
                cursor.execute('select max(request_date) '
                               f'from {TABLE_M_VIEW_REQUEST} '
                               'where view_name = %s;', [view_name])
                row = cursor.fetchone()
                request_date = row[0] if row else None

                concurency_clause = ''
                from apps.materialized_views.app_vars import CONCURRENCY_UPDATE
                if CONCURRENCY_UPDATE.val():
                    concurency_clause = ' CONCURRENTLY'
                cursor.execute(f'refresh materialized view{concurency_clause} {view_name};')

                if request_date is not None:
                    cursor.execute(f'delete from {TABLE_M_VIEW_REQUEST} '
                                   'where view_name = %s and request_date <= %s',
                                   [view_name, request_date])
                else:
                    cursor.execute(f'delete from {TABLE_M_VIEW_REQUEST} '
                                   'where view_name = %s',
                                   [view_name])
                dt_now = timezone.now()
                cursor.execute(f'insert into {TABLE_M_VIEW} '
                               '(view_name, refresh_date, status) '
                               'values (%s, %s, %s) '
                               'on conflict (view_name) do update set refresh_date = %s, '
                               'status = %s;',
                               [view_name, dt_now, MaterializedView.VIEW_STATUS_UPDATED,
                                dt_now, MaterializedView.VIEW_STATUS_UPDATED])

    def request_refresh(self, view_name: str):
        """
        Put a request on refreshing the specified materialized view.
        Requests are simple table rows: view name + date.
        We don't do any updates but only inserts to avoid
        any row locking or where clauses. In theory this should speed up the request putting.

        :param view_name:
        :return:
        """
        with connection.cursor() as cursor:
            cursor.execute(
                f'insert into {TABLE_M_VIEW_REQUEST} '
                '(view_name, request_date) '
                'values (%s, %s)',
                [view_name, timezone.now()])

    def request_refresh_by_model_class(self, view_model_class: Type[models.Model]):
        self.request_refresh(view_model_class._meta.db_table)

    def plan_refreshes(self, log: ProcessLogger, refresh_task_name: str,
                       plan_task_func: Callable[[str, datetime], None]):
        """
        Checks if there are materialized view refresh requests older than N seconds and plans the refreshing.
        The requests are inserted into the corresponding table by the document loading routines or any other
        code which changes the data on which these views are based.
        Maybe they will be replaced by a DB trigger in future.
        :param plan_task_func:
        :param log
        :return:
        """

        from apps.materialized_views.app_vars import REFRESH_DELAY
        refresh_delay_sec = REFRESH_DELAY.val()
        to_refresh = []
        with connection.cursor() as cursor:
            cursor.execute(f'''select view_name, max(request_date) 
                               from {TABLE_M_VIEW_REQUEST}
                               where to_jsonb(view_name) not in 
                                     (select args->0 from task_task where name = %s and own_status = %s) 
                               group by view_name''', (refresh_task_name, PENDING))
            for view_name, max_request_date in cursor.fetchall():  # type: str, datetime
                if timezone.now() - max_request_date > timedelta(seconds=refresh_delay_sec):
                    to_refresh.append(view_name)

        # Here we use PG advisory locks to prevent planning the materialized view refresh it the refresh
        # is already being executed.
        # The same lock is acquired in refresh_materialized_view() by any Celery worker (maybe on a different machine)
        # which is running the refresh of the same view.

        # And the following code running in Celery-beat on the master machine checks is the "refresh" is in progress
        # by trying to acquire the lock.

        for view_name in to_refresh:
            with transaction.atomic():
                # We need to execute it in a separate transaction to release the PG advisory lock
                # before executing plan_task_func.
                # Cursor is closed on the transaction end. So we initialize it here and don't re-use.
                with connection.cursor() as cursor:
                    locked = self.advisory_lock_by_relation_name(cursor, view_name)

            if locked:
                log.info(f'Planning refresh for materialized view {view_name}.')
                plan_task_func(view_name)
