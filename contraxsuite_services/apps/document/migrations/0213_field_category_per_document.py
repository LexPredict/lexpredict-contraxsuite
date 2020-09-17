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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import uuid
from typing import Dict, List, Tuple

from django.conf import settings
from django.db import migrations, connection


class DocFieldCategory:
    def __init__(self, id: int, name: str, order: int, export_key: str, document_type_id: str):
        self.id = id
        self.name = name
        self.order = order
        self.export_key = export_key
        self.document_type_id = document_type_id

    def clone(self, new_doctype_id: str):  # DocFieldCategory
        return DocFieldCategory(self.id, self.name, self.order, self.export_key, new_doctype_id)

    def insert_record(self, cursor) -> int:
        cursor.execute('''INSERT INTO document_documentfieldcategory 
                          (name, "order", export_key, document_type_id) 
                          VALUES (%s, %s, %s, %s) RETURNING id;''',
                       (self.name, self.order, uuid.uuid4(), self.document_type_id))
        return cursor.fetchone()[0]


def clone_categories(_apps, _schema_editor):
    doctype_by_category = {}  # type: Dict[int, str]
    existing = []  # type: List[DocFieldCategory]
    cat_by_id = {}  # type: Dict[int, DocFieldCategory]
    # key: [doc_type_id, cat_name], value: [category, [field_ids]]
    cloned = {}  # type: Dict[Tuple[str, str], Tuple[DocFieldCategory, List[str]]]

    with connection.cursor() as cursor:
        cursor.execute(f'''
            select f.uid, f.category_id, f.document_type_id from document_documentfield f
            inner join document_documentfield f2 on f.document_type_id != f2.document_type_id
            and f.category_id = f2.category_id;''')
        doc_field_cat = [(str(fid), catid, str(doctype))
                         for fid, catid, doctype in cursor.fetchall()]

        cursor.execute(f'''
                    select id, name, "order", export_key, document_type_id
                    from document_documentfieldcategory;''')
        for row in cursor.fetchall():
            cat = DocFieldCategory(row[0], row[1], row[2], row[3], row[4])
            cat_by_id[cat.id] = cat
            existing.append(cat)

        for cat in existing:
            if cat.document_type_id:
                doctype_by_category[cat.id] = cat.document_type_id
                continue
            for fid, cat_id, doctype_id in doc_field_cat:
                if cat_id == cat.id:
                    doctype_by_category[cat.id] = doctype_id
                    break

        for fid, cat_id, doctype_id in doc_field_cat:
            cat_doctype = doctype_by_category.get(cat_id)
            if cat_doctype and cat_doctype == doctype_id:
                continue
            orig = cat_by_id[cat_id]
            cat_key = (doctype_id, orig.name,)
            cloned_cat_fields = cloned.get(cat_key)
            if cloned_cat_fields:
                cloned_cat_fields[1].append(fid)
            else:
                cloned_cat = orig.clone(doctype_id)
                cloned[cat_key] = (cloned_cat, [fid], )

        # clone categories in DB
        for new_cat, field_ids in cloned.values():
            new_id = new_cat.insert_record(cursor)
            field_ids = ','.join([f"'{id}'" for id in set(field_ids)])
            cursor.execute(f'''UPDATE document_documentfield SET
                               category_id = %s where uid in ({field_ids});''',
                           (new_id,))


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('document', '0212_detect_limit_count'),
    ]

    operations = [
        migrations.RunPython(
            clone_categories, reverse_code=migrations.RunPython.noop
        )
    ]
