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

from typing import Dict, Any, Iterable

from django.contrib.postgres.aggregates.general import StringAgg
from django.db import connection
from django.db.models import Min, Max
from django.utils.timezone import now

from apps.common.singleton import Singleton
from apps.common.sql_commons import escape_column_name
from apps.common.utils import dictfetchone
from apps.document.constants import DocumentGenericField, FieldSpec
from apps.document.models import Document
from apps.rawdb.constants import FIELD_CODE_DOC_ID, FIELD_CODE_ASSIGNEE_ID, \
    FIELD_CODE_ASSIGNEE_NAME, FIELD_CODE_ASSIGN_DATE, FIELD_CODE_STATUS_NAME, TABLE_NAME_PREFIX
from apps.rawdb.repository.base_raw_db_repository import BaseRawDbRepository

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: check exclude_hidden_always_fields in build_field_handlers()
@Singleton
class RawDbRepository(BaseRawDbRepository):
    DEFAULT_FIELD_CODE_FILTER = {FIELD_CODE_DOC_ID}

    def update_documents_assignee(self,
                                  doc_ids: Iterable[int],
                                  assignee_id: int) -> int:
        from apps.users.models import User
        if not doc_ids:
            return 0
        assignee_name = User.objects.get(pk=assignee_id).name \
            if assignee_id else None
        col_values = {FIELD_CODE_ASSIGNEE_ID: assignee_id,
                      FIELD_CODE_ASSIGN_DATE: now(),
                      FIELD_CODE_ASSIGNEE_NAME: assignee_name}

        return self.update_rawdb_column_values(doc_ids, col_values)

    def update_documents_status(self,
                                doc_ids: Iterable[int],
                                status_id: int) -> int:
        if not doc_ids:
            return 0
        from apps.common.models import ReviewStatus
        status = ReviewStatus.objects.get(pk=status_id)  # type: ReviewStatus
        col_values = {FIELD_CODE_STATUS_NAME: status.name}
        return self.update_rawdb_column_values(doc_ids, col_values)

    def update_rawdb_column_values(self,
                                   doc_ids: Iterable[int],
                                   col_values: Dict[str, Any]) -> int:
        if not doc_ids:
            return 0
        # documents are supposed to be of the same type
        doc_type = Document.all_objects.filter(pk__in=doc_ids).values_list(
            'document_type__code', flat=True)[:1].get()  # type: str
        table_name = doc_fields_table_name(doc_type)

        doc_ids_str = ','.join([str(i) for i in doc_ids])
        start_clause = f'UPDATE "{table_name}" SET'
        up_clause = ', '.join([f'"{col}"=%s' for col in col_values])
        where_clause = f'WHERE "{FIELD_CODE_DOC_ID}" IN ({doc_ids_str})'
        query_text = f'{start_clause}\n{up_clause}\n{where_clause};'
        param_values = [col_values[c] for c in col_values]

        with connection.cursor() as cursor:
            cursor.execute(query_text, param_values)
            return cursor.rowcount

    def get_generic_values(self, doc: Document, generic_values_to_fill: FieldSpec = None) \
            -> Dict[str, Any]:
        # If changing keys of the returned dictionary - please change field code constants
        # in apps/rawdb/field_value_tables.py accordingly (FIELD_CODE_CLUSTER_ID and others)

        document_qs = Document.all_objects.filter(pk=doc.pk)

        annotations = {}

        if DocumentGenericField.cluster_id.specified_in(generic_values_to_fill):
            annotations['cluster_id'] = Max('documentcluster')

        if generic_values_to_fill is True:
            annotations['parties'] = StringAgg('textunit__partyusage__party__name',
                                               delimiter=', ', distinct=True)
            annotations['min_date'] = Min('textunit__dateusage__date')
            annotations['max_date'] = Max('textunit__dateusage__date')

        # if a Document was suddenly removed to this time
        if not document_qs.exists():
            raise Document.DoesNotExist

        values = {}
        if annotations:
            values = document_qs.annotate(**annotations).values(*annotations.keys()).first()  # type: Dict[str, Any]

        if generic_values_to_fill is True:
            # max_currency = CurrencyUsage.objects.filter(text_unit__document_id=doc.pk) \
            #     .order_by('-amount').values('currency', 'amount').first()  # type: Dict[str, Any]

            # use raw sql as the query above sometimes hangs up to 1 minute
            max_currency_sql = '''
                SELECT c.currency, MAX(c.amount) amount
                FROM extract_currencyusage c
                INNER JOIN document_textunit dtu ON c.text_unit_id = dtu.id
                WHERE dtu.document_id = {}
                GROUP BY c.currency ORDER BY amount DESC limit 1;'''.format(doc.pk)
            with connection.cursor() as cursor:
                cursor.execute(max_currency_sql)
                max_currency = dictfetchone(cursor)

                values['max_currency'] = max_currency
                values['max_currency_name'] = max_currency['currency'] if max_currency else None
                values['max_currency_amount'] = max_currency['amount'] if max_currency else None

        return values


def doc_fields_table_name(document_type_code: str) -> str:
    return escape_column_name(TABLE_NAME_PREFIX + document_type_code)
