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

from lexnlp.nlp.en.segments.sentences import pre_process_document
from apps.task.utils.nlp.parsed_text_quality_estimator import ParsedTextQualityEstimator
from django.test import TestCase

from tests.testutils import load_resource_document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestParsedTextQualityEstimator(TestCase):
    def test_estimate_dense_text(self):
        text = load_resource_document('parsing/pdf_malformat_parsed_default.txt', 'utf-8')
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        self.assertGreater(estim.extra_line_breaks_prob, 50)

        text = load_resource_document('parsing/pdf_malformat_parsed_stripper.txt', 'utf-8')
        estim = estimator.estimate_text(text)
        self.assertLess(estim.extra_line_breaks_prob, 30)

    def test_estimate_text_abusing_headers(self):
        text = load_resource_document('parsing/text_abusing_headers.txt', 'utf-8')
        text = pre_process_document(text)
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        self.assertLess(estim.extra_line_breaks_prob, 50)

    def test_estimate_fishy_header(self):
        text = """
Notwithstanding anything in this Section (B) of Article IV to the contrary, in the event any such disruption to Shmenant's operations and use of the demised premises is attributable to Landlord's negligence, or that of its agents, contractors, servants or employees, or is attributable to a breach by Landlord of its obligations under this lease, and if such disruption shall materially impair Shmenant's use of the demised premises for a period in excess of five (5) business days in duration, then a just proportion of the Rent, according to the nature and extent of the impairment to Shmenant's operation and use of the demised premises shall abate for any such period of time from the date of disruption which is in excess of said five (5) business days in duration.



ARTICLE V


RENT"""
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        self.assertLess(estim.extra_line_breaks_prob, 50)
