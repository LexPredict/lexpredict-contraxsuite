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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
from django.test import TestCase
from apps.common.log_utils import ProcessLogger, ConsoleLogger
from typing import List, Dict
from apps.document.field_detection.csv_regexps_field_detection_strategy import CsvRegexpsDetectionCache, \
    CsvRegexpsFieldDetectionStrategy
from apps.document.models import DocumentFieldMultilineRegexDetector, DocumentField, Document


class CsvRegexpsDetectionCacheMock(CsvRegexpsDetectionCache):
    event_list = []  # type: List[str]
    detector_by_field = {}  # type: Dict[str, DocumentFieldMultilineRegexDetector]

    @classmethod
    def get_detector_hash(cls, field_id: str):
        if field_id not in cls.detector_by_field:
            return ''
        detector = cls.detector_by_field[field_id]
        return detector.csv_checksum or ''

    @classmethod
    def get_detector_object(cls, field_id: str) -> DocumentFieldMultilineRegexDetector:
        detector = cls.detector_by_field[field_id]
        cls.event_list.append(f'detector #{detector.document_field.code} is loaded')
        return detector

    @classmethod
    def save_detector_settings(cls, detector: DocumentFieldMultilineRegexDetector):
        cls.event_list.append(f'detector #{detector.document_field.code} is saved')


class CsvRegexpsFieldDetectionStrategyMock(CsvRegexpsFieldDetectionStrategy):
    detecting_cache = CsvRegexpsDetectionCacheMock
    text_by_doc_id = {}  # type: Dict[str, str]

    @classmethod
    def get_document_text(cls, doc: Document) -> str:
        return cls.text_by_doc_id[doc.pk]


doc_field = DocumentField()
logger = ConsoleLogger()


def setup_mock():
    doc_field.uid = 'ABCDEF'
    doc_field.code = 'client'

    csv_text = """
    ,value,pattern
    0,"Big Bank & Company (004578) (Knight, Bobby (Charlotte); Bryant, Koby (Charlotte); Williams, Gary (Charlotte); Johnson, Magic (Charlotte); Lobo, Rebecca (Charlotte))","\bbig\s{1,5}bank\s{1,5}.{1,5}\s{1,5}company\s{1,5}(004578)\b"
    1,"Family Name Limited (173437) (Tanner, Rebecca (Houston); Saget, Bob (Houston))","family\s{1,5}name\s{1,5}\(173437\)"
    2,"Financial Services & Co. (015607) (Spelling, Tori (Chicago); Priestley, Jason (Dallas); Perry, Luke (New York); Doherty, Shannon (Chicago); Garth, Jenny (Chicago))","\bfinancial\s{1,5}services\s{1,5}.{1,5}(015607)\b"
    3,"Food Wholsale, Inc. (056230) (Jenner, Bruce (Chicago))","\bfood\s{1,5}wholsale,(056230)\b"
    4,"All Eyes Communications (018951) (Moore, Michael (New York); Tarantino, Quentin (San Francisco); Lee, Spike (New York); Levinson, Barry (Charlotte))","\ball\s{1,5}eyes\s{1,5}communications\s{1,5}(018951)\b"
    5,"Joe Smith Archives, LLC d/b/a Foxtrot (085292) (Flay, Bobby (New York))","\bfoxtrot\s{1,5}(085292)\b
    \bjoe\s{1,5}smith\s{1,5}archives\b" """

    detector = DocumentFieldMultilineRegexDetector()
    detector.csv_content = csv_text
    detector.document_field = doc_field
    detector.update_checksum()
    CsvRegexpsDetectionCacheMock.detector_by_field[doc_field.uid] = detector


setup_mock()


class TestCsvRegexpsDetectionCache(TestCase):
    def test_detect_field_value(self):
        doc = Document()
        doc.pk = 'A'
        CsvRegexpsFieldDetectionStrategyMock.text_by_doc_id = {doc.pk: """
            Collateral: Enigma Corp
            Client ref: "Diane" D.O.O. 
            """}

        found_entity = CsvRegexpsFieldDetectionStrategyMock.detect_field_value(
            logger, doc, doc_field, {})
        self.assertIsNone(found_entity)

        CsvRegexpsFieldDetectionStrategyMock.text_by_doc_id = {doc.pk: """
                    Collateral: Family Name  (173437) 
                    Client ref: "Diane" D.O.O. 
                    """}

        found_entity = CsvRegexpsFieldDetectionStrategyMock.detect_field_value(
            logger, doc, doc_field, {})
        self.assertIsNotNone(found_entity)

    def test_get_detector_wo_cache(self):
        CsvRegexpsDetectionCacheMock.PATTERNS_BY_FIELD = {}
        CsvRegexpsDetectionCacheMock.event_list = []
        detectors = CsvRegexpsDetectionCacheMock.get_detectors(doc_field.uid, self.log_message)
        self.assertEqual(6, len(detectors))
        self.assertEqual('detector #client is loaded', CsvRegexpsDetectionCacheMock.event_list[0])
        self.assertEqual(1, len(CsvRegexpsDetectionCacheMock.event_list))

        # second query is from cache
        detectors = CsvRegexpsDetectionCacheMock.get_detectors(doc_field.uid, self.log_message)
        self.assertEqual(6, len(detectors))
        # no more loading from DB and building detectors
        self.assertEqual(1, len(CsvRegexpsDetectionCacheMock.PATTERNS_BY_FIELD))
        self.assertEqual(1, len(CsvRegexpsDetectionCacheMock.event_list))

    def test_changed_detectors_are_reloaded(self):
        # init cache
        CsvRegexpsDetectionCacheMock.PATTERNS_BY_FIELD = {}
        CsvRegexpsDetectionCacheMock.event_list = []
        CsvRegexpsDetectionCacheMock.get_detectors(doc_field.uid, self.log_message)
        self.assertEqual(1, len(CsvRegexpsDetectionCacheMock.event_list))

        # update detector in "DB"
        detector = CsvRegexpsDetectionCacheMock.detector_by_field[doc_field.uid]
        detector.csv_content += ' '
        detector.update_checksum()

        # another query should go to "DB"
        detectors = CsvRegexpsDetectionCacheMock.get_detectors(doc_field.uid, self.log_message)
        self.assertEqual(6, len(detectors))
        self.assertEqual(2, len(CsvRegexpsDetectionCacheMock.event_list))

    def log_message(self, msg, e=None):
        print(f'message: {msg}, ex: {e}')
