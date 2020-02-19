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
from unittest import TestCase

from apps.similarity.chunk_similarity_task import DocumentChunkSimilarityProcessor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestDocumentChunkSimilarityProcessor(TestCase):
    def non_test_document_level(self):
        tsk = TaskStub()
        proc = DocumentChunkSimilarityProcessor(
            tsk,
            should_delete=False,
            project_id=62,
            search_similar_documents=True,
            search_similar_text_units=False,
            similarity_threshold=75,
            use_idf=True,
            term_type='WORDS')
        proc.process_pack()

    def non_test_unit_level(self):
        tsk = TaskStub()
        proc = DocumentChunkSimilarityProcessor(
            tsk,
            should_delete=False,
            project_id=None,
            search_similar_documents=False,
            search_similar_text_units=True,
            similarity_threshold=75,
            use_idf=True
        )
        proc.process_pack()


class TaskStub:
    def __init__(self):
        self.progress = 0
        self.own_progress = 0
        self.push_steps = 0

    def log_info(self, text: str):
        print(text)

    def log_debug(self, text: str):
        print(text)

    def save(self, **kwargs):
        pass

    def is_sub_task(self):
        return False

    def set_push_steps(self, value: int):
        pass

    def push(self):
        pass
