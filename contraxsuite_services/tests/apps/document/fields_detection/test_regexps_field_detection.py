from tests.django_test_case import *
from apps.document.field_type_registry import init_field_type_registry
from apps.document.repository.base_field_detector_repository import BaseFieldDetectorRepository
from typing import Union, List
from django.db.models import QuerySet
from apps.document.repository.base_text_unit_repository import BaseTextUnitRepository
from unittest import TestCase
from apps.document.fields_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.models import Document, TextUnit, DocumentFieldDetector, DocumentField


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
        cached_fields = {'area_size': 2542.0}

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
                detect_field_values(None, doc, field, cached_fields)
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

