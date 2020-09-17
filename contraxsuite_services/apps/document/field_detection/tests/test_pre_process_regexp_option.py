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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from tests.django_test_case import *
import regex as re
from unittest import TestCase
from apps.document.field_detection.regexps_field_detection import CsvDetectorImporter


class TestRegexpsOnlyFieldDetectionStrategy(TestCase):
    def test_fred(self):
        importer = self.make_importer()
        self.assertEqual(r'(^|\b)fred(\b|,).{1,7}(\b|$)', importer.pre_process_regexp_option(['Fred Inc.'])[0])
        self.assertEqual(r'(^|\b)fred\b.{1,5}sons(\b|,).{1,7}(\b|$)', importer.pre_process_regexp_option(['Fred and Sons, Inc.'])[0])

    def test_replace_conjunction(self):
        importer = self.make_importer()
        self.assertEqual(r'(^|\b)m\b.{1,3}m(\b|$)', importer.pre_process_regexp_option(['M&M'])[0])
        self.assertEqual(r'(^|\b)m\b.{1,3}m(\b|$)', importer.pre_process_regexp_option(['M &M'])[0])
        self.assertEqual(r'(^|\b)mandm(\b|$)', importer.pre_process_regexp_option(['MandM'])[0])
        self.assertEqual(r'(^|\b)mand\s{1,5}m(\b|$)', importer.pre_process_regexp_option(['Mand M'])[0])
        self.assertEqual(r'(^|\b)m\b.{1,5}m(\b|$)', importer.pre_process_regexp_option(['M  and M'])[0])

    def test_remove_comp_abbreviation(self):
        importer = self.make_importer()
        importer.wrap_in_wordbreaks = False
        text = 'Financial Services & Co. (015607)'
        s_lines = importer.pre_process_regexp_option([text])
        self.assertEqual(1, len(s_lines))
        self.assertEqual(r'financial\s{1,5}services\b.{1,3}(\b|,).{1,6}\(015607\)', s_lines[0])

        reg = re.compile(s_lines[0], re.IGNORECASE)
        matches = 0
        for _ in reg.finditer(text):
            matches += 1
        self.assertEqual(1, matches)

    def test_comp_abbr_space_extra(self):
        importer = self.make_importer()
        importer.wrap_in_wordbreaks = False
        text = 'Food Wholsale, Inc. (056230)'
        self.assertEqual('food\\s{1,5}wholsale(\\b|,).{1,7}\\(056230\\)',
                         importer.pre_process_regexp_option([text])[0])

    def test_fix_regexp(self):
        importer = self.make_importer()
        text = "Joe Smith Archives, LLC d/b/a Foxtrot Inc. (085292)"
        s_lines = importer.pre_process_regexp_option([text])
        self.assertEqual(2, len(s_lines))
        self.assertEqual(r'(^|\b)joe\s{1,5}smith\s{1,5}archives(\b|,).{1,7}(\b|$)', s_lines[0])
        self.assertEqual(r'(^|\b)foxtrot(\b|,).{1,7}\(085292\)(\b|$)', s_lines[1])

        text = 'Doherty, Shannon (Chicago)'
        s_lines = importer.pre_process_regexp_option([text])
        self.assertEqual(1, len(s_lines))
        self.assertEqual(r'(^|\b)doherty\s{1,5}shannon\s{1,5}\(\s{1,5}chicago\s{1,5}\)(\b|$)', s_lines[0])

    def test_regex_recognizes_source(self):
        src_list = [
            ('Retail Store A', 1,),
            ('Big Bank AB', 1,),
            ('Acme Capital, Inc.', 1,),
            ('Lowe & Swayze', 1,),
            ('Big Bank & Company (004578)', 1,),
            ('Family Name Limited (173437)', 1,),
            ('Financial Services & Co. (015607)', 1,),
            ('Food Wholsale, Inc. (056230)', 1,),
            ('All Eyes Communications (018951)', 1,),
            ('Joe Smith Archives, LLC d/b/a Foxtrot (085292)', 2,),
        ]
        importer = self.make_importer()
        importer.wrap_in_wordbreaks = True

        for phrase, target_ct in src_list:
            ptrns = importer.pre_process_regexp_option([phrase])
            self.assertEqual(target_ct, len(ptrns), f'"{phrase}" produced {len(ptrns)} patterns, expected {target_ct}')
            matches = 0
            for ptrn in ptrns:
                rg = re.compile(ptrn, re.IGNORECASE)
                for _ in rg.finditer(phrase):
                    matches += 1
            self.assertEqual(target_ct, matches, f'"{phrase}" gives {matches} matches, expected {target_ct}')

    @staticmethod
    def make_importer() -> CsvDetectorImporter:
        return CsvDetectorImporter(
            None,  # logger
            None,  # document_field
            False,  # drop_previous_field_detectors
            False,  # update_field_choice_values
            csv_contains_regexps=False,
            selected_columns='A, B: A',
            wrap_in_wordbreaks=True)
