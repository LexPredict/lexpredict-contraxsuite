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
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
from apps.document.field_detection.regexps_field_detection import RegexpsOnlyFieldDetectionStrategy
from apps.document.value_extraction_hints import ValueExtractionHint
from apps.document.field_detection.detector_field_matcher import DetectorFieldMatcher
from apps.document.models import DocumentField, TextUnit, TextUnitText, DocumentFieldDetector, TextParts, Document
from apps.document.field_type_registry import init_field_type_registry


init_field_type_registry()


class TestRegexpsOnlyFieldDetectionStrategy(TestCase):
    def test_extract_from_textunit_empty(self):
        text = ''
        ctx = RegexTestContext(text, 'string')
        ants = RegexpsOnlyFieldDetectionStrategy.extract_from_textunit(
            ctx.text_unit, ctx.field, [ctx.matcher])
        self.assertEqual(0, len(ants))

    def test_extract_from_textunit_match(self):
        text = '''“Required Lenders” means, as of any date of determination, 
Lenders holding more than 50% of the sum of (a) Outstanding Amount of 
the Term Loans and DDTLs and (b) aggregate  
unused Commitments; but if at least three unaffiliated Lenders exist, Required Lenders must include  
at least two unaffiliated Lenders.'''
        ctx = RegexTestContext(text, 'string')
        ants = RegexpsOnlyFieldDetectionStrategy.extract_from_textunit(
            ctx.text_unit, ctx.field, [ctx.matcher])
        self.assertEqual(1, len(ants))

    def test_extract_from_textunit_after_match(self):
        text = '''“Required Lenders” means, as of any date of determination, 
Lenders holding more than 50% of the sum of (a) Outstanding Amount of 
the Term Loans and DDTLs and (b) aggregate  
unused Commitments; but if at least three unaffiliated Lenders exist, Required Lenders must include  
at least two unaffiliated Lenders.'''
        ctx = RegexTestContext(text, 'string')
        ctx.field.value_regexp = r'\s+(l|L)enders\s+'
        ctx.detector.text_part = TextParts.FULL.value
        ctx.detector.detected_value = None
        ants = RegexpsOnlyFieldDetectionStrategy.extract_from_textunit(
            ctx.text_unit, ctx.field, [ctx.matcher])
        self.assertEqual(1, len(ants))

        ctx.detector.text_part = TextParts.AFTER_REGEXP.value
        ants = RegexpsOnlyFieldDetectionStrategy.extract_from_textunit(
            ctx.text_unit, ctx.field, [ctx.matcher])
        self.assertEqual(0, len(ants))


class RegexTestContext:
    def __init__(self, text: str, field_type: str):
        self.document = Document()
        self.field = DocumentField()
        self.field.type = field_type

        self.text_unit = TextUnit()
        self.text_unit.document = self.document
        self.text_unit.textunittext = TextUnitText()
        self.text_unit.textunittext.text = text
        self.text_unit.location_start = 1001
        self.text_unit.location_end = self.text_unit.location_start + len(text)

        self.detector = DocumentFieldDetector()
        self.detector.regexps_pre_process_lower = True
        self.detector.include_regexps = 'at\\s{1,5}least\\s{1,5}(two|2).{1,15}unaffiliated.{1,15}lenders\n' + \
            '(two|2).{1,30}lenders.{1,200}(not.{1,50}affiliate|affiliate.{1,100}(one|1|single))'
        self.detector.definition_words = 'required lenders\nrequired revolving lenders\n' + \
                                    'required revolving credit lenders\nrequired term lenders\n' + \
                                    'requisite lenders\nrequisite revolving lenders\n' + \
                                    'required class lenders\nrequired ddtl lenders'
        self.detector.detected_value = 'AFFILIATED'
        self.detector.text_part = TextParts.FULL.value
        self.detector.extraction_hint = ValueExtractionHint.TAKE_FIRST

        self.matcher = DetectorFieldMatcher(self.detector)
