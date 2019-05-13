from typing import List, Any, Tuple, Optional, Iterable

from django.contrib.postgres.aggregates.general import StringAgg

from apps.document import field_types
from apps.document.models import DocumentField, ClassifierModel, Document
from apps.extract.models import CurrencyUsage, DateUsage, PartyUsage


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

    def get_values(self, doc: Document, text: str) -> List[Tuple[Any, Optional[int], Optional[int]]]:
        """
        Locates field values in text - either in a sentence or in a whole document text
        (depending on 'by_sentence' flag).
        :param doc: Document in which the location is done
        :param text: Sentence or whole document text.
        :return: List of tuples: (value, location_start, location_end)
        """
        raise NotImplemented()


class PartiesField(PythonCodedField):
    code = 'generic.Parties'
    title = 'Parties'
    type = field_types.StringField.code
    detect_per_text_unit = False

    def get_values(self, doc: Document, text: str) -> List[Tuple[Any, Optional[int], Optional[int]]]:
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

    def get_values(self, doc: Document, text: str) -> List[Tuple[Any, Optional[int], Optional[int]]]:
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

    def get_values(self, doc: Document, text: str) -> List[Tuple[Any, Optional[int], Optional[int]]]:
        for v in DateUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('date') \
                .values_list('date', flat=True):
            return [(v, None, None)]


class MaxDateField(PythonCodedField):
    code = 'generic.LatestDate'
    title = 'Latest Date'
    type = field_types.DateField.code
    detect_per_text_unit = False

    def get_values(self, doc: Document, text: str) -> List[Tuple[Any, Optional[int], Optional[int]]]:
        for v in DateUsage.objects.filter(text_unit__document_id=doc.id) \
                .order_by('-date') \
                .values_list('date', flat=True):
            return [(v, None, None)]
        return []


PYTHON_CODED_FIELDS = [PartiesField(), MinDateField(), MaxDateField(), MaxCurrencyField()]
