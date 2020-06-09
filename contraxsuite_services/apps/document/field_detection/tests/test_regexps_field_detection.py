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
from typing import Union, List, Optional, Any
from django.db.models import QuerySet

from apps.document.field_type_registry import init_field_type_registry
from apps.document.repository.base_field_detector_repository import BaseFieldDetectorRepository
from apps.document.repository.base_text_unit_repository import BaseTextUnitRepository
from apps.document.field_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.models import Document, TextUnit, DocumentFieldDetector, DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitTextMock:
    def __init__(self, text: str):
        self.text = text


class TextUnitMock:
    def __init__(self,
                 text: str,
                 pk: int,
                 location_start: int = 0,
                 location_end: int = 100):
        self.textunittext = TextUnitTextMock(text)
        self.pk = pk
        self.location_start = location_start
        self.location_end = location_end

    def is_sentence(self):
        return True


class TestRegexpsOnlyFieldDetectionStrategy(TestCase):
    """
    Test regexp based field values detecting
    """
    def test_fred(self):
        detected = self.detect_values_in_document([
            TextUnitMock("Fred, Inc.", 10),
            TextUnitMock("Fredof, Inc.", 20),
            TextUnitMock("Fred,Inc.", 30),
            TextUnitMock("fred, Inc.", 40),
        ],
            self.make_doc_field_detector(include_regexps=r'\bfred(\b|,).{1,7}\b',
                                         detected_value='fred')
        )

        self.assertIsNotNone(detected)
        self.assertEqual(3, len(detected.annotations))

    def test_order_field_detection(self) -> None:
        detected = self.detect_values_in_document([
                TextUnitMock("But those cushion's velvet lining", 10),
                TextUnitMock("She shall press! Ah! Nevermore...", 20)
            ],
            self.make_doc_field_detector()
        )

        self.assertIsNotNone(detected)
        self.assertEqual(['shall'], detected.field_value)
        self.assertEqual(1, len(detected.annotations))
        self.assertEqual('shall', detected.annotations[0].annotation_value)

    def detect_values_in_document(self,
                                  text_units: List[TextUnitMock],
                                  detector: DocumentFieldDetector):
        init_field_type_registry()
        doc = self.setup_document(text_units)
        field = DocumentField()
        field.requires_text_annotations = False
        field.stop_words = None
        field.text_unit_type = 'sentences'
        field.type = 'multi_choice'
        field.allow_values_not_specified_in_choices = True

        text_unit_repo = MockTextUnitRepository()
        text_unit_repo.units = text_units
        for tu in text_unit_repo.units:
            tu.document = doc
            tu.unit_type = field.text_unit_type

        detect_repo = MockFieldDetectorRepository()
        detect_repo.detectors = [detector]

        old_tu_repo = RegexpsOnlyFieldDetectionStrategy.text_unit_repo
        RegexpsOnlyFieldDetectionStrategy.text_unit_repo = text_unit_repo
        old_repo_detect = RegexpsOnlyFieldDetectionStrategy.field_detector_repo
        RegexpsOnlyFieldDetectionStrategy.field_detector_repo = detect_repo

        try:
            detected = RegexpsOnlyFieldDetectionStrategy. \
                detect_field_value(None, doc, field, {})
        finally:
            RegexpsOnlyFieldDetectionStrategy.text_unit_repo = old_tu_repo
            RegexpsOnlyFieldDetectionStrategy.field_detector_repo = old_repo_detect
        return detected

    def make_doc_field_detector(self,
                                exclude_regexps: Optional[str] = None,
                                include_regexps: Optional[str] = None,
                                detected_value: Optional[str] = None) -> DocumentFieldDetector:
        detector = DocumentFieldDetector()
        detector.exclude_regexps = exclude_regexps if exclude_regexps is not None else 'cushion'
        detector.include_regexps = include_regexps if include_regexps is not None else r'(?<=\D{3,3}\s\D{5,5}\s)\D+'
        detector.detected_value = detected_value if detected_value is not None else 'shall'
        detector.extraction_hint = 'detected'
        return detector

    def setup_document(self, text_units: List[TextUnitMock]) -> Any:
        doc = MockDocument(full_text='\n'.join([t.textunittext.text for t in text_units]))
        return doc


class MockDocument:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._full_text = kwargs.get('full_text')

    @property
    def full_text(self):
        return self._full_text


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
