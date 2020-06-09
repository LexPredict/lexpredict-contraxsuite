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
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Optional

from django.db import connection
from django.db.models import QuerySet


def stringify_queryset(qs: QuerySet) -> str:
    sql, params = qs.query.sql_with_params()
    with connection.cursor() as cursor:
        cursor.execute('EXPLAIN ' + sql, params)
        raw_sql =  cursor.db.ops.last_executed_query(cursor, sql, params)
    raw_sql = raw_sql[len('EXPLAIN '):]
    return raw_sql


class QuerySetWoCache(QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_records = 0

    @staticmethod
    def wrap(qs: QuerySet):
        qs.__class__ = QuerySetWoCache
        return qs

    def __getitem__(self, k):
        """Retrieve an item or slice from the set of results."""
        if not isinstance(k, (int, slice)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if isinstance(k, slice):
            qs = self._chain()
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            qs.query.set_limits(start, stop)
            return list(qs)[::k.step] if k.step else qs

        qs = self._chain()
        qs.query.set_limits(k, k + 1)
        qs._fetch_all()
        return qs._result_cache[0]


class CustomCountQuerySet(QuerySet):
    @staticmethod
    def wrap(qs: QuerySet):
        qs.__class__ = CustomCountQuerySet
        return qs

    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model=model, query=query, using=using, hints=hints)
        self.optional_count_query = None  # type: Optional[str]

    def _clone(self):
        """
        Return a copy of the current QuerySet. A lightweight alternative
        to deepcopy().
        """
        c = self.__class__(model=self.model, query=self.query.chain(), using=self._db, hints=self._hints)
        c._sticky_filter = self._sticky_filter
        c._for_write = self._for_write
        c._prefetch_related_lookups = self._prefetch_related_lookups[:]
        c._known_related_objects = self._known_related_objects
        c._iterable_class = self._iterable_class
        c._fields = self._fields
        if hasattr(self, 'optional_count_query'):
            c.optional_count_query = self.optional_count_query
        return c

    def set_optional_count_query(self, query: Optional[str] = None):
        self.optional_count_query = query

    # TODO: delete this
    def count(self):
        """
        Unlike base "count" this one limits count
        by "limit" parameter in query
        """
        if hasattr(self, 'optional_count_query') and self.optional_count_query:
            return self.get_count_custom_sql()
        return super().count()

    def get_count_custom_sql(self):
        """
        Perform a COUNT() query using custom SQL
        """
        #if self._result_cache is not None:
        #    return len(self._result_cache)

        with connection.cursor() as cursor:
            cursor.execute(self.optional_count_query)
            row = cursor.fetchone()
        return row[0]
