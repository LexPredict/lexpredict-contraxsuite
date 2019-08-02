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

from typing import List, Any, Tuple, Optional, Iterable

from django.contrib.postgres.aggregates.general import StringAgg

from apps.document import field_types
from apps.document.models import DocumentField, ClassifierModel, Document
from apps.extract.models import CurrencyUsage, DateUsage, PartyUsage
from apps.common.log_utils import ProcessLogger

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PythonCodedField:
    code = ''
    title = ''
    type = ''

    uses_cached_document_field_values = False

    # If true - detect field values separately in each sentence/paragraph.
    # If false - run get_values() against the whole document and next try to find matching text unit (sentence)
    #            for each detected value.
    # see apps.document.tasks.detect_field_values_for_python_coded_field()
    detect_per_text_unit = True

    def train_document_field_detector_model(self,
                                            document_field: DocumentField,
                                            train_data_project_ids: List,
                                            use_only_confirmed_field_values: bool = False,
                                            train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
        return None

    def get_values(self, log: ProcessLogger, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        """
        Locates field values in text - either in a sentence or in a whole document text
        (depending on 'by_sentence' flag).
        :param log
        :param field Configured document field
        :param doc: Document in which the location is done
        :param text: Sentence or whole document text.
        :return: List of tuples: (value, location_start, location_end)
        """
        raise NotImplementedError()


class PartiesField(PythonCodedField):
    code = 'generic.Parties'
    title = 'Parties'
    type = field_types.StringField.code
    detect_per_text_unit = False

    def get_values(self, log, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        v = PartyUsage.objects.filter(text_unit__document_id=doc.id) \
            .aggregate(value=StringAgg('party__name', delimiter=', ', distinct=True))
        if v:
            return [(v['value'], None, None)]
        else:
            return []


class MaxCurrencyField(PythonCodedField):
    code = 'generic.MaxCurrency'
    title = 'Max Currency'
    type = field_types.MoneyField.code
    detect_per_text_unit = False

    def get_values(self, log, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        for v in CurrencyUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('-amount') \
                .values('currency', 'amount'):
            return [(v, None, None)]
        return []


class MinDateField(PythonCodedField):
    code = 'generic.EarliestDate'
    title = 'Earliest Date'
    type = field_types.DateField.code
    detect_per_text_unit = False

    def get_values(self, log, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        for v in DateUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('date') \
                .values_list('date', flat=True):
            return [(v, None, None)]


class MaxDateField(PythonCodedField):
    code = 'generic.LatestDate'
    title = 'Latest Date'
    type = field_types.DateField.code
    detect_per_text_unit = False

    def get_values(self, log, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        for v in DateUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('-date') \
                .values_list('date', flat=True):
            return [(v, None, None)]
        return []


PYTHON_CODED_FIELDS = [PartiesField(), MinDateField(), MaxDateField(), MaxCurrencyField()]
