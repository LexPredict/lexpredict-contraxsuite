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

from tests.django_test_case import *
from apps.analyze.models import DocumentClassifierSuggestion, DocumentClassification
from django.test import TestCase
from apps.analyze.ml.classify import ClassifyDocuments
from apps.document.models import Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestClassifyDoc2Vec(TestCase):
    def non_test_classify(self):
        class_name = 'category'
        queryset = Document.objects.filter(project__description='OpenEdgar import')
        engine = ClassifyDocuments()
        classifier = engine.build_classifier(
            train_queryset=queryset,  # restrict train data
            class_name=class_name,  # restrict train data
            classifier_assessment=True,  # create accuracy metrics (TextUnitClassifierAssessment objects)
            metric_pos_label='true',  # this is required if classifier_assessment=True
            classifier_algorithm='RandomForestClassifier',
            classifier_name='Open Edgar Doc2Vec classifier',  # may be omitted
            classify_by=['text'],  # list or sentence like 'term' for one source
            metric_average='weighted'
        )

        count = engine.run_classifier(
            classifier,
            test_queryset=Document.objects.filter(project__description='OpenEdgar import'),
            min_confidence=90)
        print(count)

    def non_test_category(self):
        source_classes = list(DocumentClassification.objects.filter(
            class_name='category').values_list('document_id', 'class_value'))
        source_classes = {id: c for id, c in source_classes}

        suggest_classes = list(DocumentClassifierSuggestion.objects.filter(
            class_name='category').values_list('document_id', 'class_value'))
        suggest_classes = {id: c for id, c in suggest_classes}

        hits, misses = (0, 0,)
        for id in source_classes:
            if source_classes[id] == suggest_classes.get(id):
                hits += 1
            else:
                misses += 1

        print(f'{hits} hits, {misses} misses')
