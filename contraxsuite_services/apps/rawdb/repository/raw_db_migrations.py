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

from typing import List

from django.db import connection

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def add_rawdb_migration_column(field_name: str,
                               field_type: str):
    """
    This should be much faster than reindexing all "rawdb" tables.
    1 - get document type codes -> cache table names
    2 - for each document "raw" table add field document_contract_class
         document_contract_class: character varying
    """
    from apps.rawdb.repository.raw_db_repository import doc_fields_table_name

    table_names: List[str] = []
    with connection.cursor() as cursor:
        cursor.execute('SELECT "code" FROM document_documenttype;')
        for code in cursor.fetchall():
            table_names.append(doc_fields_table_name(code[0]))

        for table_name in table_names:
            if not check_table_exists(cursor, table_name):
                continue
            cursor.execute(
                f'''DO $$ 
                    BEGIN
                        BEGIN
                            ALTER TABLE {table_name} ADD COLUMN {field_name} {field_type};
                        EXCEPTION
                            WHEN duplicate_column THEN RAISE NOTICE 
                                'column {field_name} already exists in {table_name}.';
                        END;
                    END;
                    $$
                ''')


def check_table_exists(cursor, table_name: str) -> bool:
    cursor.execute(f"SELECT to_regclass('{table_name}');")
    for r in cursor.fetchall():
        if r[0]:
            return True
    return False
