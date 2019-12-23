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

import pandas as pd
import numpy as np

from django.db.models import Sum, Value, Q, Case, When, IntegerField

from apps.document.models import Document, TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EmptyDataSetError(Exception):

    def __init__(self, *args, **kwargs):
        self.feature_source = kwargs.pop('feature_source', None)
        super().__init__(*args, **kwargs)


class Features:
    """
    Encapsulates info about features for certain model objects
    """
    def __init__(self,
                 feature_df: pd.DataFrame,
                 term_frequency_matrix: np.array,
                 item_index: list,
                 feature_names: list,
                 item_names: list,
                 unqualified_item_ids: list,
                 unqualified_item_names: list):
        self.feature_df = feature_df
        self.term_frequency_matrix = term_frequency_matrix
        self.item_index = item_index
        self.feature_names = feature_names
        self.item_names = item_names
        self.unqualified_item_ids = unqualified_item_ids
        self.unqualified_item_names = unqualified_item_names


class DocumentFeatures:
    """
    Collects features for Documents.
    Transforms a model queryset into features.
    :Example:
        >>> feature_obj = DocumentFeatures(
        ...:        queryset=some_queryset,
        ...:        project_id=18,
        ...:        feature_source="term",
        ...:        unit_type="sentence").get_features()
    Returns Feature object (see above for its signature)
    """
    source_model = Document
    project_filter_key = 'project_id'
    unit_type_filter = 'textunit__unit_type'

    source_fields = dict(
        source_type='source_type',
        document_type='document_type',
        metadata='documentmetadata__metadata',
        date='textunit__dateusage__date',
        definition='textunit__definitionusage__definition',
        duration='textunit__datedurationusage__duration_days',
        court='textunit__courtusage__court__name',
        currency_name='textunit__currencyusage__currency',
        currency_value='textunit__currencyusage__amount',
        term='textunit__termusage__term__term',
        party='textunit__partyusage__party__name',
        geoentity='textunit__geoentityusage__entity__name')

    aggregation_functions = dict(
        source_type=Value('source_type'),
        document_type=Value('document_type'),
        metadata=Value('documentmetadata__metadata'),
        date=Sum('textunit__dateusage__count'),
        definition=Sum('textunit__definitionusage__count'),
        duration=Sum('textunit__datedurationusage__count'),
        court=Sum('textunit__courtusage__count'),
        currency_name=Sum('textunit__currencyusage__count'),
        currency_value=Sum('textunit__currencyusage__count'),
        term=Sum('textunit__termusage__count'),
        party=Sum('textunit__partyusage__count'),
        geoentity=Sum('textunit__geoentityusage__count'))

    def __init__(self,
                 queryset=None,
                 project_id=None,
                 unit_type='sentence',
                 feature_source='term',
                 skip_unqualified_values=True):
        """
        :param queryset: Document/TextUnit queryset
        :param project_id: int
        :param unit_type: str - one of "sentence", "paragraph"
        :param feature_source: str or list[str] - source name - e.g. "term", or ["term", "date"]
        :param skip_unqualified_values: bool - whether skip empty rows from resulted queryset
        """
        self.queryset = queryset
        self.project_id = project_id
        self.unit_type = unit_type
        self.feature_source = [feature_source] if isinstance(feature_source, str) else feature_source
        self.skip_unqualified_values = skip_unqualified_values
        self.check()

    def check(self):
        """
        Validate incoming data
        """
        if self.queryset is None and self.project_id is None:
            raise RuntimeError('Provide either "queryset" or "project_id" argument.')
        if self.unit_type not in ('sentence', 'paragraph'):
            raise RuntimeError('The "unit_type" argument should be one of "sentence", "paragraph".')
        if not isinstance(self.feature_source, (list, tuple)):
            raise RuntimeError('The "feature_source" argument should be of string or list type.')
        elif set(self.feature_source).difference(set(self.source_fields)):
            raise RuntimeError('The "feature_source" argument should contain only {}, but it includes {}'.format(
                str(list(self.source_fields.keys())), str(self.feature_source)))

    def get_queryset(self):
        """
        Get target model queryset (Document vs TextUnit)
        :return: queryset
        """
        target_qs = self.queryset or self.source_model.objects
        target_qs = target_qs.filter()
        if self.project_id:
            target_qs = target_qs.filter(**{self.project_filter_key: self.project_id})
        if not target_qs.exists():
            msg = 'Initial queryset {}is empty.'.format(
                'of chosen project_id={} '.format(self.project_id) if self.project_id else '')
            raise EmptyDataSetError(msg, feature_source=self.feature_source)
        return target_qs.distinct()

    def get_feature_df(self):
        """
        Transform incoming data into pandas dataframe
        :return: tuple(features pandas.DataFrame, unqualified item id list)
        """
        # prepare features dataframe
        df = pd.DataFrame()

        target_qs = self.get_queryset()
        target_id_field = 'id'
        counter = 'counter'

        for feature_source_item in self.feature_source:

            # get aggregation queryset parameters for .annotate function
            source_field = self.source_fields[feature_source_item]
            aggregation_function = self.aggregation_functions[feature_source_item]
            aggregation_function.filter = Q(**{self.unit_type_filter: self.unit_type})
            aggregation = {counter: aggregation_function}

            # use bool value for missing metadata
            if feature_source_item == 'metadata':
                aggregation = {
                    counter: Case(When(**{source_field + '__isnull': False}, then=Value(1)),
                                  default=Value(0), output_field=IntegerField())}

            # prepare feature_source_item-specific values queryset with total counts per ID/term
            term_source_qs = target_qs \
                .order_by(target_id_field, source_field) \
                .values(target_id_field, source_field) \
                .annotate(**aggregation)

            # skip unqualified rows with zeros
            if self.skip_unqualified_values:
                term_source_qs = term_source_qs.filter(**{counter + '__gt': 0})

            if not term_source_qs.exists():
                continue

            # unpack nested metadata values into features
            if feature_source_item == 'metadata':
                term_source_qs = [
                    {'id': item['id'], source_field: '%s: %s' % (k, str(v)), counter: 1} for item in
                    term_source_qs for k, v in item[source_field].items()]

            # feature_source_item-specific dataframe
            df_ = pd.DataFrame(list(term_source_qs)).dropna()

            # use number of days since min value as feature value
            if feature_source_item == 'date':
                min_value = df_[source_field].min().toordinal() - 1
                df_[counter] = df_.apply(lambda x: x[source_field].toordinal() - min_value, axis=1)

            # use amount value as feature value
            elif feature_source_item in ['duration', 'currency_value']:
                df_[counter] = df_.apply(lambda x: x[source_field], axis=1)

            # transform dataframe
            dft = df_.pivot(index=target_id_field, columns=source_field, values=counter)

            # name columns by feature_source item like "term(account)", "duration(30)"
            dft.columns = ["%s(%s)" % (feature_source_item, str(i)) for i in dft.columns]

            # join  feature_source_item-specific dataframe into results dataframe
            df = df.join(dft, how='outer')

        if df.empty:
            msg = 'No features of chosen "feature_source" options {} detected. ' \
                  'Empty Data Set.'.format(str(self.feature_source))
            raise EmptyDataSetError(msg, feature_source=self.feature_source)

        # item ids not included in feature df which don't have features at all
        initial_id_set = set(target_qs.values_list(target_id_field, flat=True))
        feature_id_set = set(df.index.tolist())
        unqualified_item_ids = sorted(list(initial_id_set.difference(feature_id_set)))

        if not self.skip_unqualified_values and unqualified_item_ids:
            unqualified_items_df = pd.DataFrame(index=unqualified_item_ids)
            df = df.join(unqualified_items_df, how='outer')

        return df, unqualified_item_ids

    def get_features(self):
        """
        Aggregator method to transform incoming queryset into features and indexes
        :return: Features object
        """
        feature_df, unqualified_item_ids = self.get_feature_df()

        term_frequency_matrix = feature_df.fillna(0).values
        item_index = feature_df.index.tolist()
        feature_names = feature_df.columns.tolist()
        item_names = self.get_item_names(item_index)
        unqualified_item_names = self.get_item_names(unqualified_item_ids)

        res = Features(feature_df, term_frequency_matrix, item_index, feature_names, item_names,
                       unqualified_item_ids, unqualified_item_names)

        return res

    def get_item_names(self, item_index):
        """
        Get Document names corresponding to passed id set
        :param item_index: list(id)
        :return: list(str)
        """
        document_id_to_name = dict(Document.objects.filter(id__in=item_index).values_list('id', 'name'))
        return [document_id_to_name[i] for i in item_index]


class TextUnitFeatures(DocumentFeatures):
    """
    Collects features for TextUnits
    See DocumentFeatures docstring.
    """

    source_model = TextUnit
    project_filter_key = 'document__project_id'
    unit_type_filter = 'unit_type'

    source_fields = dict(
        source_type='document__source_type',
        document_type='document__document_type',
        metadata='document__documentmetadata__metadata',
        court='courtusage__court__name',
        currency_name='currencyusage__currency',
        currency_value='currencyusage__amount',
        date='dateusage__date',
        definition='definitionusage__definition',
        duration='datedurationusage__duration_days',
        term='termusage__term__term',
        party='partyusage__party__name',
        geoentity='geoentityusage__entity__name')

    aggregation_functions = dict(
        source_type=Value('document__source_type'),
        document_type=Value('document__document_type'),
        metadata=Value('document__documentmetadata__metadata'),
        date=Sum('dateusage__count'),
        definition=Sum('definitionusage__count'),
        duration=Sum('datedurationusage__count'),
        court=Sum('courtusage__count'),
        currency_name=Sum('currencyusage__count'),
        currency_value=Sum('currencyusage__count'),
        term=Sum('termusage__count'),
        party=Sum('_partyusage__count'),
        geoentity=Sum('geoentityusage__count'))

    def get_item_names(self, item_index):
        """
        Get TextUnit names corresponding to passed id set
        :param item_index: list(id)
        :return: list(str)
        """
        text_unit_id_to_name = dict([(tu.id, str(tu)) for tu in TextUnit.objects.filter(id__in=item_index)])
        return [text_unit_id_to_name[i] for i in item_index]
