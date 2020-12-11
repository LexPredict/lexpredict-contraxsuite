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


from typing import List, Set, Optional

from apps.analyze.models import TextUnitSimilarity
from apps.document.models import TextUnit, Document


class SimilarityObjectReference:

    @classmethod
    def ensure_unit_similarity_model_refs(cls,
                                          records: List[TextUnitSimilarity],
                                          project_id: Optional[int] = None):
        """
        The method sets references to "document_a, document_b, project_a and project_b"
        """
        if not records:
            return
        if project_id:
            for r in records:
                r.project_a_id = project_id
                r.project_b_id = project_id

        unit_ids: Set[int] = set()
        for r in records:
            if not r.document_a_id or not r.project_a_id:
                unit_ids.add(r.text_unit_a_id)
            if not r.document_b_id or not r.project_b_id:
                unit_ids.add(r.text_unit_b_id)

        if not unit_ids:
            return

        document_unit_query = TextUnit.objects.filter(project_id=project_id, pk__in=unit_ids) if project_id \
            else TextUnit.objects.filter(pk__in=unit_ids)
        document_unit = document_unit_query.values_list('pk', 'document_id')
        document_by_unit = {u:d for u, d in document_unit}

        # set document_ids
        docs_to_query: Set[int] = set()
        for r in records:
            r.document_a_id = r.document_a_id or document_by_unit[r.text_unit_a_id]
            r.document_b_id = r.document_b_id or document_by_unit[r.text_unit_b_id]
            if not r.project_a_id:
                docs_to_query.add(r.document_a_id)
            if not r.project_b_id:
                docs_to_query.add(r.document_b_id)

        # set project ids
        if not docs_to_query:
            return
        documents_query = Document.all_objects.filter(pk__in=docs_to_query)
        documents = documents_query.values_list('pk', 'project_id')
        project_by_doc = {d: p for d, p in documents}
        for r in records:
            r.project_a_id = r.project_a_id or project_by_doc[r.document_a_id]
            r.project_b_id = r.project_b_id or project_by_doc[r.document_b_id]
