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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
from django.db import connection
from apps.common.sql_commons import drop_constraints_for_table_and_generate_restore_queries, \
    drop_indexes_for_table_and_generate_restore_query


TABLE_NAME = 'analyze_textunitsimilarity'


CONSTRAINT_LIST = ['ALTER TABLE public."analyze_textunitsimilarity" ADD CONSTRAINT analyze_textunitsimi_document_a_id_46a26942_fk_document_ FOREIGN KEY (document_a_id) REFERENCES document_document(id) DEFERRABLE INITIALLY DEFERRED;',
                   'ALTER TABLE public."analyze_textunitsimilarity" ADD CONSTRAINT analyze_textunitsimi_document_b_id_bd73876d_fk_document_ FOREIGN KEY (document_b_id) REFERENCES document_document(id) DEFERRABLE INITIALLY DEFERRED;',
                   'ALTER TABLE public."analyze_textunitsimilarity" ADD CONSTRAINT analyze_textunitsimi_project_a_id_05f097a1_fk_project_p FOREIGN KEY (project_a_id) REFERENCES project_project(id) DEFERRABLE INITIALLY DEFERRED;',
                   'ALTER TABLE public."analyze_textunitsimilarity" ADD CONSTRAINT analyze_textunitsimi_project_b_id_5faaaabb_fk_project_p FOREIGN KEY (project_b_id) REFERENCES project_project(id) DEFERRABLE INITIALLY DEFERRED;', 'ALTER TABLE public."analyze_textunitsimilarity" ADD CONSTRAINT analyze_textunitsimi_text_unit_a_id_e6a9f0aa_fk_document_ FOREIGN KEY (text_unit_a_id) REFERENCES document_textunit(id) DEFERRABLE INITIALLY DEFERRED;', 'ALTER TABLE public."analyze_textunitsimilarity" ADD CONSTRAINT analyze_textunitsimi_text_unit_b_id_0800d70d_fk_document_ FOREIGN KEY (text_unit_b_id) REFERENCES document_textunit(id) DEFERRABLE INITIALLY DEFERRED;']


INDEX_LIST = ['CREATE INDEX analyze_textunitsimilarity_created_date_e5c44037 ON public.analyze_textunitsimilarity USING btree (created_date);',
              'CREATE INDEX analyze_textunitsimilarity_document_a_id_46a26942 ON public.analyze_textunitsimilarity USING btree (document_a_id);',
              'CREATE INDEX analyze_textunitsimilarity_document_b_id_bd73876d ON public.analyze_textunitsimilarity USING btree (document_b_id);',
              'CREATE INDEX analyze_textunitsimilarity_project_a_id_05f097a1 ON public.analyze_textunitsimilarity USING btree (project_a_id);', 'CREATE INDEX analyze_textunitsimilarity_project_b_id_5faaaabb ON public.analyze_textunitsimilarity USING btree (project_b_id);', 'CREATE INDEX analyze_textunitsimilarity_text_unit_a_id_e6a9f0aa ON public.analyze_textunitsimilarity USING btree (text_unit_a_id);', 'CREATE INDEX analyze_textunitsimilarity_text_unit_b_id_0800d70d ON public.analyze_textunitsimilarity USING btree (text_unit_b_id);']


def restore_textunitsim_constraints(_apps, _schema_editor):
    started = datetime.datetime.now()
    queries = CONSTRAINT_LIST + INDEX_LIST
    with connection.cursor() as cursor:
        for i, query in enumerate(queries):
            print(f'Restoring constraints, step [{i + 1} / {len(queries)}]')
            cursor.execute(query)
    elapsed = (datetime.datetime.now() - started).total_seconds()
    print(f'Restoring constraints took {elapsed}s')


def drop_textunitsim_constraints(_apps, _schema_editor):
    schema_name = 'public'
    with connection.cursor() as cursor:
        print(f'{TABLE_NAME}: dropping constraints')
        drop_constraints_for_table_and_generate_restore_queries(
            cursor, TABLE_NAME, schema_name=schema_name)
        drop_indexes_for_table_and_generate_restore_query(
            cursor, TABLE_NAME, schema_name=schema_name)
