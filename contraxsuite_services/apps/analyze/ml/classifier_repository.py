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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Iterable, Union, Optional, List, Any, Tuple

from django.db.models import QuerySet

from apps.analyze.models import DocumentVector, DocumentClassifierAssessment, TextUnitClassifierAssessment, \
    DocumentClassifier, TextUnitClassifier
from apps.common.singleton import Singleton
from apps.document.models import DocumentText, Document


class ClassifierRepository:
    def get_fulltext_by_doc(self, project_ids: Iterable[int]):
        return DocumentText.objects.filter(document__project_id__in=project_ids).values_list(
            'document_id', 'full_text')

    def get_document_plain_texts(self,
                                 document_qs: Optional[Union[QuerySet, Iterable[Document]]] = None,
                                 project_ids: Optional[Iterable[int]] = None) -> Tuple[Iterable[str], int]:
        """
        returns: (text iterator, total count)
        """
        text_queryset = DocumentText.objects
        if document_qs is not None:
            text_queryset = text_queryset.filter(document__in=document_qs)
        if project_ids is not None:
            # NB: filtering by document__project_id__in takes enormous time
            document_ids = list(Document.objects.filter(project_id__in=project_ids).values_list('pk', flat=True))
            text_queryset = text_queryset.filter(document__in=document_ids)
        texts_count = text_queryset.count()
        # we return iterator() to prevent caching the query and thus loading all the texts in memory
        return text_queryset.values_list('full_text', flat=True).iterator(), texts_count

    def get_vector_document_name(self, vector: DocumentVector) -> str:
        return vector.document.name

    def save_classifier(self,
                        classifier: Union[DocumentClassifier, TextUnitClassifier]):
        classifier.save()

    def save_classifications(self,
                             model_class,
                             classifications: List[Union[DocumentClassifierAssessment,
                                                         TextUnitClassifierAssessment]]):
        model_class.objects.bulk_create(classifications)

    def save_transformer(self,
                         transformer_class: Any,
                         **kwargs) -> Any:
        return transformer_class.objects.create(**kwargs)

    def ensure_unique_name(self, name: str, model_class) -> str:
        names = set(model_class.objects.filter(
            name__startswith=name).values_list('name', flat=True))
        if name in names:
            for i in range(1000):
                name_candidate = f'{name} copy {i}'
                if name_candidate not in names:
                    return name_candidate
        return name


@Singleton
class ClassifierRepositoryBuilder:
    def __init__(self):
        self._repository = ClassifierRepository()

    @property
    def repository(self) -> ClassifierRepository:
        return self._repository
