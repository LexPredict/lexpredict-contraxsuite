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

# Standard imports
from datetime import datetime, date
from typing import List, Tuple

# Django imports
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.safestring import mark_safe

from apps.document.field_types import LinkedDocumentsField, TypedField
from apps.document.models import DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


DST_FIELD_SIMILARITY_CONFIG_ATTR = 'similar_documents_field_config'
ATTR_DST_FIELD = 'dst_field'
ATTR_FEATURE_VECTOR_FIELDS = 'feature_vector_fields'
ATTR_DATE_CONSTRAINT_FIELD = 'date_constraint_field'
ATTR_DATE_CONSTRAINT_DAYS = 'date_constraint_days'
DEFAULT_SIMILARITY_TRESHOLD = 0.9
DEFAULT_DATE_CONSTRAINT_DAYS = 10


class DocumentSimilarityConfig(models.Model):
    dst_field = models.OneToOneField(DocumentField,
                                     on_delete=models.CASCADE,
                                     null=False,
                                     blank=False,
                                     related_name=DST_FIELD_SIMILARITY_CONFIG_ATTR,
                                     primary_key=True)

    similarity_threshold = models.FloatField(null=False, blank=False, default=DEFAULT_SIMILARITY_TRESHOLD)

    date_constraint_field = models.ForeignKey(DocumentField, on_delete=models.DO_NOTHING, null=True, blank=True)

    date_constraint_days = models.IntegerField(blank=True, null=True, default=DEFAULT_DATE_CONSTRAINT_DAYS,
                                               validators=[MinValueValidator(0)])

    @staticmethod
    def validate(dst_field: DocumentField, date_constraint_field: DocumentField, date_constraint_days: int) \
            -> List[Tuple[str, str]]:
        document_type = dst_field.document_type
        feature_vector_fields = dst_field.depends_on_fields.all()
        res = list()

        if date_constraint_days is not None and date_constraint_days < 1:
            res.append((ATTR_DATE_CONSTRAINT_DAYS, 'Date constraint days should be either empty or a '
                                                   'positive integer.'))

        if date_constraint_field is not None and date_constraint_field.document_type_id != document_type.pk:
            res.append((ATTR_DATE_CONSTRAINT_FIELD, 'Date constraint field should be owned by the same document type'
                                                    'as the destination field.'))

        if date_constraint_field is not None and date_constraint_days is None:
            res.append((ATTR_DATE_CONSTRAINT_DAYS, 'Date constraint days number should not be empty if the date '
                                                   'constraint field is assigned.'))

        if date_constraint_field is not None:
            example_value = TypedField.by(date_constraint_field).example_python_value()
            if not isinstance(example_value, (date, datetime)):
                res.append((ATTR_DATE_CONSTRAINT_FIELD, 'Type of the date constraint field should be date or datetime'))

        if dst_field.type != LinkedDocumentsField.code:
            res.append((ATTR_DST_FIELD, 'Destination field should be of type {0}'.format(LinkedDocumentsField.code)))

        if not feature_vector_fields:
            res.append((ATTR_FEATURE_VECTOR_FIELDS, 'Feature vector fields list can not be empty.'))

        wrong_doc_type_fields = list()
        for f in feature_vector_fields:
            if f.document_type_id != dst_field.document_type_id:
                wrong_doc_type_fields.append(f.code)
        if wrong_doc_type_fields:
            res.append((ATTR_FEATURE_VECTOR_FIELDS, mark_safe('''All feature vector fields should be owned by
                    the same document type as the destination field: {dst_field_type}.<br />
                    The following fields are owned by different document type(s):<br />{bad_fields}'''
                                                              .format(bad_fields='<br />'.join(wrong_doc_type_fields),
                                                                      dst_field_type=document_type.code))))
        return res or None

    def self_validate(self):
        problems = self.validate(self.dst_field, self.date_constraint_field, self.date_constraint_days)
        if problems:
            raise RuntimeError('\n'.join(['{0}: {1}'.format(attr, err) for attr, err in problems]))

    def __str__(self):
        return 'Similarity Config: {field}'.format(field=self.dst_field.code)
