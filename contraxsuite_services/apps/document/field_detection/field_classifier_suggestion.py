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


from django.utils.timezone import now
from apps.analyze.models import DocumentClassifier, DocumentClassifierSuggestion
from apps.document.models import DocumentField, ClassifierModel, Document


def store_classification_suggestion(field: DocumentField,
                                    doc: Document,
                                    class_value: str,
                                    confidence: float):
    suggest = DocumentClassifierSuggestion()
    suggest.classifier = ensure_document_classifier(field)
    suggest.document = doc
    suggest.classifier_run = now()
    suggest.classifier_confidence = confidence
    suggest.class_name = field.code
    suggest.class_value = class_value
    suggest.save()


def ensure_document_classifier(field: DocumentField) -> DocumentClassifier:
    clsf_name = f'{field.document_type.code}_{field.code}_field_classifier'
    clsf_class_name = field.code
    clsf_query = DocumentClassifier.objects.filter(name=clsf_name, class_name=clsf_class_name)

    if clsf_query.count():
        return clsf_query.order_by('-pk')[0]

    clsf = DocumentClassifier()
    clsf.name = clsf_name
    clsf.version = str(now())
    clsf.class_name = clsf_class_name
    clsf.model_object = bytearray()
    clsf.is_active = False
    clsf.save()
    return clsf
