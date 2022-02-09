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
from django.test import TestCase
from typing import List, Optional, Union
from django.db.models import QuerySet

from apps.document.field_type_registry import init_field_type_registry
from apps.document.repository.base_field_detector_repository import BaseFieldDetectorRepository
from apps.document.repository.base_text_unit_repository import BaseTextUnitRepository
from apps.document.field_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.models import Document, TextUnit, DocumentFieldDetector, DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MockTextUnit:
    def __init__(self,
                 text: str,
                 pk: int,
                 location_start: int = 0,
                 location_end: int = 100,
                 language: str = 'en'):
        self.text = text
        self.pk = pk
        self.location_start = location_start
        self.location_end = location_end
        self.language = language

    def is_sentence(self):
        return True


class MockDocument:
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.pk = kwargs.get('pk', -1)
        self.name = kwargs.get('name', 'Mock Document')
        self._full_text = kwargs.get('full_text')

    @property
    def full_text(self):
        return self._full_text


class MockTextUnitRepository(BaseTextUnitRepository):
    def __init__(self):
        self.units: List[TextUnit] = []

    def get_doc_text_units(
        self,
        doc: Document,
        text_unit_type: str
    ) -> Union[QuerySet, List[TextUnit]]:

        return sorted(
            self.units,
            key=lambda u: (u.location_start, u.pk),
            reverse=False
        )


class MockFieldDetectorRepository(BaseFieldDetectorRepository):
    def __init__(self):
        self.detectors: List[DocumentFieldDetector] = []

    def get_field_detectors(self, field: DocumentField) -> \
            Union[QuerySet, List[DocumentFieldDetector]]:
        return self.detectors


class TestRegexpsOnlyFieldDetectionStrategy(TestCase):
    """
    Test regexp-based field value detection
    """
    def test_fred(self) -> None:
        detected = self.detect_values_in_document(
            [
                MockTextUnit("Fred, Inc.", 10),
                MockTextUnit("Fredof, Inc.", 20),
                MockTextUnit("Fred,Inc.", 30),
                MockTextUnit("fred, Inc.", 40),
            ],
            self.make_doc_field_detector(
                include_regexps=r'\bfred(\b|,).{1,7}\b',
                detected_value='fred'
            )
        )

        self.assertIsNotNone(detected)
        self.assertEqual(3, len(detected.annotations))

    def test_order_field_detection(self) -> None:
        detected = self.detect_values_in_document(
            [
                MockTextUnit("But those cushion's velvet lining", 10),
                MockTextUnit("She shall press! Ah! Nevermore...", 20)
            ],
            self.make_doc_field_detector(),
            type='string',
            value_regexp='.+'
        )

        self.assertIsNotNone(detected)
        self.assertEqual('press! Ah! Nevermore...', detected.field_value)
        self.assertEqual(1, len(detected.annotations))
        self.assertEqual('press! Ah! Nevermore...', detected.annotations[0].annotation_value)

    def test_detection_limits(self) -> None:
        detected = self.detect_values_in_document(
            [
                MockTextUnit('The quick brown fox jumps over a lazy dog.', i)
                for i in range(1, 6, 1)
            ],
            self.make_doc_field_detector(
                include_regexps=r'\bb.{1,3}n\sfox\b',
                detected_value='brown fox',
                detect_limit_count=3
            ),
        )

        self.assertIsNotNone(detected)
        self.assertEqual(3, len(detected.annotations))
        self.assertEqual('brown fox', detected.field_value)
        for i in range(0, 3, 1):
            self.assertEqual('brown fox', detected.annotations[i].annotation_value)

    def test_geographyfield_detection(self) -> None:
        # TODO: this only produces one annotation, even when two are present.
        detected = self.detect_values_in_document(
            list(
                map(
                    lambda s: MockTextUnit(f'This document shall be {s}', -1),
                    [
                        'followed to the letter.'
                        'governed by United States law.',
                        # 'interpreted according to the law of the United States.',
                        'United States'
                    ]
                )
            ),
            self.make_doc_field_detector(
                include_regexps='governed\\s{1,5}by\r\n'
                                'accordance.{1,25}law\r\n'
                                'interpreted.{1,10}according.{1,10}law.{1,5}of',
                detected_value='United States'
            ),
            type='string'
        )

        self.assertIsNotNone(detected)
        self.assertEqual(1, len(detected.annotations))
        self.assertEqual('United States', detected.field_value)

    def test_uppercase(self) -> None:
        detected_by_case = []
        for case_flag in [False, True]:
            detected = self.detect_values_in_document(
                [
                    MockTextUnit('The quick brown fOx jumps over a lazy dog.', 1)
                ],
                self.make_doc_field_detector(
                    include_regexps=r'\bb.{1,3}n\sfox\b',
                    detected_value='brown fox',
                    regexps_pre_process_lower=case_flag
                ),
            )
            detected_by_case.append((case_flag, detected,))

        self.assertIsNone(detected_by_case[0][1])

        self.assertIsNotNone(detected_by_case[1][1])
        self.assertEqual(1, len(detected_by_case[1][1].annotations))

    def test_definition_words(self):
        detected = self.detect_values_in_document(
            [
                MockTextUnit('''Buthrzd d"uatc-\nmunicate the acceptance of the offer to the between 
                so-called 'authorized" and unauthre\nofferor. ''', 1)
            ],
            self.make_doc_field_detector(
                include_regexps='',
                detected_value='error',
                regexps_pre_process_lower=True,
                definition_words='account\nauthorized'
            ),
            type='string'
        )
        self.assertIsNotNone(detected)

    def test_definition_words_mix_case(self):
        detected = self.detect_values_in_document(
            [
                MockTextUnit('''Buthrzd d"uatc-\nmunicate the acceptance of the offer to the between 
                so-called 'Authorized" and unauthre\nofferor. ''', 1)
            ],
            self.make_doc_field_detector(
                include_regexps='',
                detected_value='error',
                regexps_pre_process_lower=True,
                definition_words='account\nauthorized'
            ),
            type='string'
        )
        self.assertIsNotNone(detected)

    def detect_values_in_document(self,
                                  text_units: List[MockTextUnit],
                                  detector: DocumentFieldDetector,
                                  **doc_field_kwargs):
        init_field_type_registry()
        field = self.make_doc_field(**doc_field_kwargs)
        detector.field = field
        doc = self.setup_document(text_units)
        detect_repo = MockFieldDetectorRepository()
        detect_repo.detectors = [detector]
        text_unit_repo = MockTextUnitRepository()
        text_unit_repo.units = text_units
        for tu in text_unit_repo.units:
            tu.document = doc
            tu.unit_type = field.text_unit_type

        old_repo_tu = RegexpsOnlyFieldDetectionStrategy.text_unit_repo
        RegexpsOnlyFieldDetectionStrategy.text_unit_repo = text_unit_repo
        old_repo_detect = RegexpsOnlyFieldDetectionStrategy.field_detector_repo
        RegexpsOnlyFieldDetectionStrategy.field_detector_repo = detect_repo

        try:
            detected = RegexpsOnlyFieldDetectionStrategy.detect_field_value(
                None, doc, field, {})
        finally:
            RegexpsOnlyFieldDetectionStrategy.text_unit_repo = old_repo_tu
            RegexpsOnlyFieldDetectionStrategy.field_detector_repo = old_repo_detect
        return detected

    @staticmethod
    def make_doc_field(**kwargs) -> DocumentField:
        doc_field_attributes = {
            'requires_text_annotations': kwargs.get('requires_text_annotations', False),
            'text_unit_type': kwargs.get('text_unit_type', 'sentence'),
            'type': kwargs.get('type', 'multi_choice'),
            'choices': kwargs.get('choices', 'brown fox\nbrown box\nfrown fox'),
            'allow_values_not_specified_in_choices': kwargs.get('choices', True)
        }

        for k, v in doc_field_attributes.items():
            if k not in kwargs:
                kwargs[k] = v
        return DocumentField(**kwargs)

    @staticmethod
    def make_doc_field_detector(exclude_regexps: Optional[str] = None,
                                include_regexps: Optional[str] = None,
                                detected_value: Optional[str] = None,
                                regexps_pre_process_lower: bool = True,
                                definition_words: Optional[str] = None,
                                detect_limit_unit='UNIT',
                                detect_limit_count=0) -> DocumentFieldDetector:
        detector = DocumentFieldDetector()
        detector.exclude_regexps = exclude_regexps if exclude_regexps is not None else 'cushion'
        detector.include_regexps = include_regexps if include_regexps is not None else r'(?<=\D{3,3}\s\D{5,5}\s)\D+'
        if detected_value is not None:
            detector.detected_value = detected_value
        detector.extraction_hint = 'TAKE_FIRST'  # 'detected'
        detector.text_part = 'INSIDE_REGEXP'
        detector.regexps_pre_process_lower = regexps_pre_process_lower
        detector.definition_words = definition_words
        detector.detect_limit_unit = detect_limit_unit
        detector.detect_limit_count = detect_limit_count
        return detector

    @staticmethod
    def setup_document(text_units: List[MockTextUnit]) -> MockDocument:
        return MockDocument(full_text='\n'.join([t.text for t in text_units]))
