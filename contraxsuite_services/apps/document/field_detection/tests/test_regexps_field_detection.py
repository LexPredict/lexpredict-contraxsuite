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

from typing import Union, List
from unittest import TestCase

from django.db.models import QuerySet

from apps.document.field_type_registry import init_field_type_registry
from apps.document.repository.base_field_detector_repository import BaseFieldDetectorRepository
from apps.document.repository.base_text_unit_repository import BaseTextUnitRepository
from apps.document.field_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.models import Document, TextUnit, DocumentFieldDetector, DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestRegexpsOnlyFieldDetectionStrategy(TestCase):
    """
    Test regexp based field values detecting
    """
    def test_order_field_detection(self) -> None:
        init_field_type_registry()
        doc = self.setup_document()
        field = DocumentField()
        field.requires_text_annotations = False
        field.stop_words = None
        field.text_unit_type = 'sentences'

        text_unit_repo = MockTextUnitRepository()
        text_unit_repo.units = [
            TextUnit(),
            TextUnit()
        ]
        text_unit_repo.units[0].text = "But those cushion's velvet lining"
        text_unit_repo.units[1].text = "She shall press! Ah! Nevermore..."
        for tu in text_unit_repo.units:
            tu.document = doc
            tu.unit_type = field.text_unit_type

        detect_repo = MockFieldDetectorRepository()

        detector = self.make_doc_field_detector()
        detect_repo.detectors = [detector]

        old_tu_repo = RegexpsOnlyFieldDetectionStrategy.text_unit_repo
        RegexpsOnlyFieldDetectionStrategy.text_unit_repo = text_unit_repo
        old_repo_detect = RegexpsOnlyFieldDetectionStrategy.field_detector_repo
        RegexpsOnlyFieldDetectionStrategy.field_detector_repo = detect_repo

        try:
            detected = RegexpsOnlyFieldDetectionStrategy.\
                detect_field_value(None, doc, field)
        finally:
            RegexpsOnlyFieldDetectionStrategy.text_unit_repo = old_tu_repo
            RegexpsOnlyFieldDetectionStrategy.field_detector_repo = old_repo_detect

        self.assertEqual(1, len(detected))

    def make_doc_field_detector(self) -> DocumentFieldDetector:
        detector = DocumentFieldDetector()
        detector.exclude_regexps = 'cushion'
        detector.include_regexps = r'(?<=\D{3,3}\s\D{5,5}\s)\D+'
        detector.detected_value = 'shall'
        detector.extraction_hint = None
        return detector

    def setup_document(self) -> Document:
        doc = Document()
        return doc


class MockTextUnitRepository(BaseTextUnitRepository):
    def __init__(self):
        self.units = []  # type: List[TextUnit]

    def get_doc_text_units(self, doc: Document, text_unit_type: str) -> \
            Union[QuerySet, List[TextUnit]]:
        #return [u for u in self.units if u.document == doc and
        #        u.unit_type == text_unit_type]
        return self.units


class MockFieldDetectorRepository(BaseFieldDetectorRepository):
    def __init__(self):
        self.detectors = []  # type: List[DocumentFieldDetector]

    def get_field_detectors(self, field: DocumentField) -> \
            Union[QuerySet, List[DocumentFieldDetector]]:
        return self.detectors
