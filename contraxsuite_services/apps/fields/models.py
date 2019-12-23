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

import pickle

from django.db import models
from django.db.models.deletion import CASCADE

from apps.document.models import Document
from apps.fields.parsing.field_annotations_classifier import SkLearnClassifierModel
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentField(models.Model):
    id = models.CharField(max_length=256, primary_key=True)


class DocumentAnnotationTag(models.Model):
    id = models.CharField(max_length=256, primary_key=True)


class ClassifierModel(models.Model):
    KIND_SENTENCES_RELATED_TO_FIELDS = 'sentences_related_to_fields'

    kind = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    document_class = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    document_field = models.ForeignKey(DocumentField, db_index=True, null=True, blank=True, on_delete=CASCADE)
    trained_model = models.BinaryField(null=True, blank=True)

    def get_trained_model_obj(self) -> SkLearnClassifierModel:
        if not self.trained_model:
            return None
        return pickle.loads(self.trained_model)

    def set_trained_model_obj(self, obj: SkLearnClassifierModel):
        self.trained_model = pickle.dumps(obj)


class ClassifierDataSetEntry(models.Model):
    field_detection_model = models.ForeignKey(ClassifierModel, db_index=True, null=False,
                                              blank=False, on_delete=CASCADE)
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)
    category = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    text = models.TextField(null=False)


class DocumentAnnotation(models.Model):
    document = models.ForeignKey(Document, db_index=True, on_delete=CASCADE)
    start = models.CharField(max_length=256)
    end = models.CharField(max_length=256)
    start_offset = models.IntegerField(null=False, blank=False)
    end_offset = models.IntegerField(null=False, blank=False)
    quote = models.TextField(null=False, blank=False)
    comment = models.CharField(max_length=1024, null=True, blank=True)
    tags = models.ManyToManyField(DocumentAnnotationTag)
    document_field = models.ForeignKey(DocumentField,
                                       db_index=True, null=True, blank=True, on_delete=CASCADE)
    user = models.ForeignKey(User, db_index=True, null=True, blank=True, on_delete=CASCADE)

    @staticmethod
    def build_auto_annotation(doc: Document, field: str, start_offset: int, end_offset: int,
                              quote: str):
        # there is some difference in offsets provided by sentences segmenter and annotator.js view
        magic_offset = 15

        return DocumentAnnotation(document=doc,
                                  document_field=DocumentField.objects.get_or_create(pk=field)[0],
                                  start='/p[1]',
                                  end='/p[1]',
                                  start_offset=start_offset + magic_offset,
                                  end_offset=end_offset + magic_offset,
                                  quote=quote)
