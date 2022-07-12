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

import datetime
import random
from collections import defaultdict
from typing import List, Set, Dict, Type, Optional

from django.db import transaction
from django.conf import settings
from django.db.models import Sum
from lexnlp.extract.all_locales import amounts, citations, courts, dates, definitions, durations, percents, money
from lexnlp.extract.en import copyright, distances, geoentities, ratios, regulations, trademarks, urls
from lexnlp.nlp.en.tokens import get_stems, get_tokens_by_regex

from apps.common.log_utils import ProcessLogger
from apps.common.model_utils.safe_bulk_create import SafeBulkCreate
from apps.document.models import TextUnitTag
from apps.extract import dict_data_cache
from apps.extract.companies_extractor import CompaniesExtractor
from apps.extract.dict_data_cache import clean_geo_config_cache
from apps.extract.locating_performance_meter import LocatingPerformanceMeter
from apps.extract.models import AmountUsage, CitationUsage, CopyrightUsage, CourtUsage, CurrencyUsage, \
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage, \
    GeoAliasUsage, GeoEntityUsage, PercentUsage, RatioUsage, RegulationUsage, \
    Party, PartyUsage, TermUsage, TrademarkUsage, UrlUsage, Usage, DocumentTermUsage, DocumentDefinitionUsage, \
    ProjectGeoEntityUsage, ProjectPartyUsage, ProjectTermUsage, ProjectDefinitionUsage
from apps.extract.term_stems import TermStemsCache
from apps.materialized_views.mat_views import MaterializedViews
from settings import DEFAULT_FLOAT_PRECISION

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MAT_VIEWS_REFRESH_ON_LOCATE_FINISHED = {
    'definition': ProjectDefinitionUsage,
    'geoentity': ProjectGeoEntityUsage,
    'party': ProjectPartyUsage,
    'term': ProjectTermUsage,
}


def request_mat_views_refresh(locate_entities: List = None):
    mat_views = MaterializedViews()
    for entity_name, model_class in MAT_VIEWS_REFRESH_ON_LOCATE_FINISHED.items():
        # 1. either no locate_entities passed - see apps.extract.locators.doc_full_delete_listener
        # 2. or passed from Locate.save_summary_on_locate_finished
        if locate_entities is None or entity_name in locate_entities:
            mat_views.request_refresh_by_model_class(model_class)


class ParseResults:
    __slots__ = ['usage_entities', 'text_unit_tags']

    def __init__(self, usage_entities: Dict[Type[Usage], List[Usage]],
                 text_unit_tags: Optional[Set[str]] = None) -> None:
        super().__init__()
        self.usage_entities = dict(
            usage_entities) if usage_entities is not None else dict()  # type: Dict[Type[Usage], List[Usage]]
        self.text_unit_tags = set(text_unit_tags) if text_unit_tags is not None else set()  # type: Set[str]

    def update_doc_project_ids(self, document_id: int, project_id: int):
        if self.usage_entities:
            for entity_list in self.usage_entities.values():
                for entity in entity_list:
                    entity.document_id = document_id
                    entity.project_id = project_id


class LocationResults:

    def __init__(self, document_initial_load: bool = False) -> None:
        self.tags = defaultdict(set)  # type: Dict[int, Set[str]]
        self.located_usage_entities = defaultdict(list)  # type: Dict[Type[Usage], List]
        self.processed_usage_entity_classes = set()  # type: Set[Type[Usage]]
        self.processed_text_unit_ids = set()  # type: Set[int]
        self.document_initial_load = document_initial_load

    def collect(self, locator: 'Locator', text_unit_id, parse_results: ParseResults):
        self.processed_text_unit_ids.add(text_unit_id)
        self.processed_usage_entity_classes.update(locator.locates_usage_model_classes)
        if parse_results:
            if parse_results.text_unit_tags:
                self.tags.update({text_unit_id: tag_str for tag_str in parse_results.text_unit_tags})
            if parse_results.usage_entities:
                self.tags[text_unit_id].add(locator.code)
                for k, v in parse_results.usage_entities.items():
                    self.located_usage_entities[k].extend(v)

    def save(self, log: ProcessLogger, user_id):
        try:
            with transaction.atomic():
                if self.processed_text_unit_ids:
                    if not self.document_initial_load:
                        TextUnitTag.objects.filter(text_unit_id__in=self.processed_text_unit_ids).delete()
                        for entity_class in self.processed_usage_entity_classes:
                            entity_class.objects.filter(text_unit_id__in=self.processed_text_unit_ids).delete()

                tag_models = []
                from apps.document.app_vars import LOCATE_TEXTUNITTAGS
                tags_saved = 0
                if LOCATE_TEXTUNITTAGS.val():
                    for text_unit_id, tags in self.tags.items():
                        for tag in tags:
                            tag_models.append(TextUnitTag(user_id=user_id,
                                                          text_unit_id=text_unit_id,
                                                          tag=tag))
                    tags_saved = SafeBulkCreate.bulk_create(TextUnitTag.objects.bulk_create, tag_models)

            # save "_usage" objects
            count = 0
            for entity_class, entities in self.located_usage_entities.items():  # type: Type[Usage], List[Usage]
                if not entities:
                    continue
                count += SafeBulkCreate.bulk_create(entity_class.objects, entities)

            log.info(
                'Stored {0} usage entities and {1} tags for {2} text units'.format(
                    count, tags_saved, len(self.processed_text_unit_ids)))
        except Exception as e:
            entities_str = '\n'.join([str(e) for e in self.processed_usage_entity_classes])
            log.error(f'Unable to store location results.\n'
                      f'Text unit ids: {self.processed_text_unit_ids}\n'
                      f'Usage models caused the problem:\n{entities_str}', exc_info=e)


class Locator:
    STRICT_DATES_PTR = 'strict_dates'

    code = None

    locates_usage_model_classes = []

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        pass

    def try_parsing(self,
                    log: ProcessLogger,
                    locate_results: LocationResults,
                    text: str,
                    text_unit_id: int,
                    text_unit_lang: str,
                    document_id: int,
                    document_project_id: int,
                    parsing_context_id: Optional[str] = None,
                    **kwargs):
        if not text:
            return
        start = datetime.datetime.now()
        try:
            parse_results = self.parse(
                log, text, text_unit_id, text_unit_lang, document_project_id,
                locate_results.document_initial_load, parsing_context_id, **kwargs)  # type: ParseResults
            if parse_results:
                parse_results.update_doc_project_ids(document_id, document_project_id)
                locate_results.collect(self, text_unit_id, parse_results)
            elapsed = (datetime.datetime.now() - start).total_seconds()

            if settings.DEBUG_TRACK_LOCATING_PERFORMANCE:
                LocatingPerformanceMeter().add_record(str(type(self).__name__),
                                                      elapsed, text_unit_id, text)
        except Exception as e:
            log.error(f'Exception caught while trying to run locator on a text unit.\n'
                      f'Locator: {self.__class__.__name__}\n'
                      f'Text unit id: {text_unit_id}\n'
                      f'Text: {text[:1024]}\n'
                      f'Text unit language: {text_unit_lang}\n', exc_info=e)

    @classmethod
    def update_document_summary(cls, log: ProcessLogger, doc_id: int, document_initial_load: bool = False):
        pass


class AmountLocator(Locator):
    code = 'amount'

    locates_usage_model_classes = [AmountUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = list(amounts.get_amount_annotations(text_unit_lang,
                                                    text,
                                                    extended_sources=False,
                                                    float_digits=DEFAULT_FLOAT_PRECISION))
        if found:
            unique = set(found)
            return ParseResults({AmountUsage: [AmountUsage(text_unit_id=text_unit_id,
                                                           amount=item.value,
                                                           amount_str=item.text[:300] if item.text else None,
                                                           count=found.count(item)
                                                           ) for item in unique]})


class CitationLocator(Locator):
    code = 'citation'
    locates_usage_model_classes = [CitationUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = list(citations.get_citation_annotations(text_unit_lang, text))
        if found:
            unique = set(found)
            return ParseResults({CitationUsage: [CitationUsage(text_unit_id=text_unit_id,
                                                               volume=item.volume,
                                                               reporter=item.reporter,
                                                               reporter_full_name=item.reporter_full_name,
                                                               page=item.page,
                                                               page2=item.page_range,
                                                               court=item.court,
                                                               year=item.year,
                                                               citation_str=item.source,
                                                               count=found.count(item)) for item in unique]})


class CourtLocator(Locator):
    code = 'court'

    locates_usage_model_classes = [CourtUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        from apps.extract.app_vars import SIMPLE_LOCATOR_TOKENIZATION
        simple_norm = SIMPLE_LOCATOR_TOKENIZATION.val(project_id=document_project_id)
        # TODO: load DE courts?
        court_config = dict_data_cache.get_court_config()
        found = [a.entity_id
                 for a in courts.get_court_annotations(
                     text_unit_lang,
                     text,
                     court_config_list=court_config,
                     text_locales=[text_unit_lang],
                     simplified_normalization=simple_norm)]
        if found:
            unique = set(found)
            return ParseResults({CourtUsage: [CourtUsage(text_unit_id=text_unit_id,
                                                         court_id=court_id,
                                                         count=found.count(court_id)) for court_id in unique]})


class DistanceLocator(Locator):
    code = 'distance'

    locates_usage_model_classes = [DistanceUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        precision = DEFAULT_FLOAT_PRECISION
        found = list(distances.get_distance_annotations(text, float_digits=precision))
        if found:
            unique = set(found)
            return ParseResults({DistanceUsage: [DistanceUsage(text_unit_id=text_unit_id,
                                                               amount=item.amount,
                                                               amount_str=item.text,
                                                               distance_type=item.distance_type,
                                                               count=found.count(item)) for item in unique]})


class DateLocator(Locator):
    code = 'date'

    locates_usage_model_classes = [DateUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        from apps.extract.app_vars import STRICT_PARSE_DATES
        strict = kwargs.get(Locator.STRICT_DATES_PTR, STRICT_PARSE_DATES.val(project_id=document_project_id))
        found = list(dates.get_date_annotations(
            text_unit_lang,
            text,
            strict=strict))
        if found:
            _all = [i.date.date() if isinstance(i.date, datetime.datetime)
                    else i.date for i in found]
            return ParseResults({DateUsage: [DateUsage(text_unit_id=text_unit_id,
                                                       date=item,
                                                       count=_all.count(item)) for item in set(_all)]})


class DefinitionLocator(Locator):
    code = 'definition'

    locates_usage_model_classes = [DefinitionUsage]

    @classmethod
    def update_document_summary(cls, log: ProcessLogger, doc_id: int,
                                document_initial_load: bool = False):
        doc_usages = list(DefinitionUsage.objects
                          .filter(text_unit__document_id=doc_id)
                          .values('definition')
                          .annotate(total_count=Sum('count'))
                          .order_by())
        if not document_initial_load:
            DocumentDefinitionUsage.objects.filter(document_id=doc_id).delete()
        DocumentDefinitionUsage.objects.bulk_create(
            [DocumentDefinitionUsage(document_id=doc_id, definition=item['definition'], count=item['total_count'])
             for item in doc_usages], ignore_conflicts=True)

    @staticmethod
    def _is_any_alphanumeric(string: str) -> bool:
        for c in string:
            if c.isalnum():
                return True
        return False

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        defs = [d for d in definitions.get_definition_annotations(text_unit_lang, text)
                if self._is_any_alphanumeric(d.name)]
        if defs:
            unique = set(defs)
            return ParseResults({DefinitionUsage:
                                     [DefinitionUsage(text_unit_id=text_unit_id,
                                                      definition=item.name.upper()
                                                      if item.name is not None else None,
                                                      count=defs.count(item)
                                                      ) for item in unique]})


class DurationLocator(Locator):
    code = 'duration'

    locates_usage_model_classes = [DateDurationUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        precision = DEFAULT_FLOAT_PRECISION
        found = list(durations.get_duration_annotations(text_unit_lang, text, float_digits=precision))
        if found:
            unique = set(found)
            return ParseResults({DateDurationUsage: [DateDurationUsage(text_unit_id=text_unit_id,
                                                                       amount=item.amount,
                                                                       amount_str=item.text,
                                                                       duration_type=item.duration_type,
                                                                       duration_days=item.duration_days,
                                                                       count=found.count(item)
                                                                       ) for item in unique]})


class CurrencyLocator(Locator):
    code = 'currency'

    locates_usage_model_classes = [CurrencyUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = list(money.get_money_annotations(
            text_unit_lang, text, float_digits=DEFAULT_FLOAT_PRECISION))
        if found:
            unique = set(found)
            return ParseResults({CurrencyUsage: [CurrencyUsage(text_unit_id=text_unit_id,
                                                               amount=item.amount,
                                                               amount_str=item.text,
                                                               currency=item.currency,
                                                               count=found.count(item)
                                                               ) for item in unique]})


class PartyLocator(Locator):
    code = 'party'

    locates_usage_model_classes = [PartyUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> Optional[ParseResults]:
        # Here we override saving logic to workaround race conditions on party creation vs party usage saving
        project_id = kwargs.get('project_id', None)
        if not document_initial_load:
            PartyUsage.objects.filter(text_unit_id=text_unit_id).delete()
        found = list(CompaniesExtractor.get_companies(
            project_id, text, count_unique=True, detail_type=True, name_upper=True,
            selected_tags=kwargs.get('selected_tags')))
        if found:
            results = []
            for _party in found:
                name, _type, type_abbr, type_label, type_desc, count = _party
                defaults = dict(
                    type=_type,
                    type_label=type_label,
                    type_description=type_desc
                )
                party, _ = Party.objects.get_or_create(
                    name=name,
                    type_abbr=type_abbr or '',
                    defaults=defaults)
                results.append(PartyUsage(text_unit_id=text_unit_id,
                                          party=party,
                                          count=count))

            return ParseResults({PartyUsage: results})


class PercentLocator(Locator):
    code = 'percent'

    locates_usage_model_classes = [PercentUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = list(percents.get_percent_annotations(
            text_unit_lang, text, float_digits=DEFAULT_FLOAT_PRECISION))
        if found:
            unique = set(found)
            return ParseResults({PercentUsage: [
                PercentUsage(text_unit_id=text_unit_id,
                             amount=item.amount,
                             amount_str=item.text,
                             unit_type=item.sign,
                             total=item.fraction,
                             count=found.count(item)) for item in unique]})


class RatioLocator(Locator):
    code = 'ratio'

    locates_usage_model_classes = [RatioUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = list(ratios.get_ratio_annotations(text,
                                                  float_digits=DEFAULT_FLOAT_PRECISION))
        if found:
            unique = set(found)
            return ParseResults({RatioUsage: [RatioUsage(text_unit_id=text_unit_id,
                                                         amount=item.left,
                                                         amount2=item.right,
                                                         amount_str=item.text,
                                                         total=item.ratio,
                                                         count=found.count(item)) for item in unique]})


class RegulationLocator(Locator):
    code = 'regulation'

    locates_usage_model_classes = [RegulationUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = list(regulations.get_regulation_annotations(text))
        if found:
            unique = set(found)
            return ParseResults({RegulationUsage: [RegulationUsage(text_unit_id=text_unit_id,
                                                                   regulation_type=item.source,
                                                                   regulation_name=item.name,
                                                                   count=found.count(item)) for item in unique]})


class CopyrightLocator(Locator):
    code = 'copyright'
    locates_usage_model_classes = [CopyrightUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        # TODO: what's the logic behind [:200] ... < 100 ?
        found = list(copyright.get_copyright_annotations(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({CopyrightUsage: [CopyrightUsage(text_unit_id=text_unit_id,
                                                                 year=item.date,
                                                                 name=item.name[:200],
                                                                 copyright_str=item.text[:200],
                                                                 count=found.count(item)
                                                                 ) for item in unique if len(item.name) < 100]})


class TrademarkLocator(Locator):
    code = 'trademark'
    locates_usage_model_classes = [TrademarkUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = [t.trademark for t in trademarks.get_trademark_annotations(text)]
        if found:
            unique = set(found)
            return ParseResults({TrademarkUsage: [TrademarkUsage(text_unit_id=text_unit_id,
                                                                 trademark=item,
                                                                 count=found.count(item)
                                                                 ) for item in unique]})


class UrlLocator(Locator):
    code = 'url'

    locates_usage_model_classes = [UrlUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        found = [u.url for u in urls.get_url_annotations(text)]
        if found:
            unique = set(found)
            return ParseResults({UrlUsage: [UrlUsage(text_unit_id=text_unit_id,
                                                     source_url=item,
                                                     count=found.count(item)) for item in unique]})


class GeoEntityLocator(Locator):
    code = 'geoentity'

    locates_usage_model_classes = [GeoEntityUsage, GeoAliasUsage]

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        priority_check = kwargs.get('priority', True)
        geo_config = dict_data_cache.get_geo_config(parsing_context_id)
        from apps.extract.app_vars import SIMPLE_LOCATOR_TOKENIZATION
        simple_norm = SIMPLE_LOCATOR_TOKENIZATION.val()
        entity_alias_pairs = list(geoentities.get_geoentities(
            text,
            geo_config,
            text_languages=[text_unit_lang],
            conflict_resolving_field='priority' if priority_check else 'none',
            simplified_normalization=simple_norm))

        entity_ids = [entity.id for entity, _alias in entity_alias_pairs]
        if entity_ids:
            unique_entities = set(entity_ids)
            alias_ids = [alias.alias_id for _entity, alias in entity_alias_pairs]
            unique_aliases = set(alias_ids)

            return ParseResults({
                GeoEntityUsage: [GeoEntityUsage(text_unit_id=text_unit_id,
                                                entity_id=idd,
                                                count=entity_ids.count(idd)) for idd in unique_entities],
                GeoAliasUsage: [GeoAliasUsage(text_unit_id=text_unit_id,
                                              alias_id=idd,
                                              count=alias_ids.count(idd)) for idd in unique_aliases if idd]})


class TermLocator(Locator):
    code = 'term'
    locates_usage_model_classes = [TermUsage]

    @classmethod
    def update_document_summary(cls, log: ProcessLogger, doc_id: int, document_initial_load: bool = False):
        doc_term_usages = list(TermUsage.objects
                               .filter(text_unit__document_id=doc_id)
                               .values('term_id')
                               .annotate(total_count=Sum('count'))
                               .order_by())
        if not document_initial_load:
            DocumentTermUsage.objects.filter(document_id=doc_id).delete()
        DocumentTermUsage.objects.bulk_create(
            [DocumentTermUsage(document_id=doc_id, term_id=item['term_id'], count=item['total_count'])
             for item in doc_term_usages], ignore_conflicts=True)

    def parse(self,
              log: ProcessLogger,
              text: str,
              text_unit_id: int,
              _text_unit_lang: str,
              document_project_id: int,
              document_initial_load: bool = False,
              parsing_context_id: Optional[str] = None,
              **kwargs) -> ParseResults:
        # w/o local caching this code takes 90% of the function call
        term_stems = TermStemsCache.get_term_stems(
            document_project_id, parsing_context_id, kwargs.get('selected_tags'))
        text_stems = ' %s ' % ' '.join(get_stems(text, lowercase=True))
        # this call would make the whole method ~5% slower
        # get_token_list(text, lowercase=True) # this
        text_tokens = list(get_tokens_by_regex(text, lowercase=True))
        term_usages = []
        for stemmed_term, data in term_stems.items():
            # stem not found in text
            if stemmed_term not in text_stems:
                continue
            # if stem has 1 variant only
            if data['length'] == 1:
                count = text_stems.count(stemmed_term)
                if count:
                    term_data = list(data['values'][0])
                    term_data.append(count)
                    term_usages.append(term_data)
            # case when f.e. stem "respons" is equal to multiple terms
            # ["response", "responsive", "responsibility"]
            else:
                for term_data in data['values']:
                    term_data = list(term_data)
                    count = text_tokens.count(term_data[0])
                    if count:
                        term_data.append(count)
                        term_usages.append(term_data)
                        # TODO: "responsibilities"

        return ParseResults({TermUsage: [
            TermUsage(text_unit_id=text_unit_id,
                      term_id=pk,
                      count=count) for _, pk, count in term_usages]})


class LocatorsCollection:
    _LOCATOR_CLASSES = [AmountLocator, CitationLocator, CopyrightLocator, CourtLocator,
                        CurrencyLocator, DurationLocator, DateLocator, DefinitionLocator,
                        DistanceLocator, GeoEntityLocator, PercentLocator, RatioLocator,
                        RegulationLocator, PartyLocator, TermLocator, TrademarkLocator,
                        UrlLocator]

    _LOCATORS = None  # type: Optional[Dict[str, Locator]]

    @classmethod
    def get_locators(cls) -> Dict[str, Locator]:
        if cls._LOCATORS:
            return cls._LOCATORS
        cls._LOCATORS = {locator_class.code: locator_class()
                         for locator_class in cls._LOCATOR_CLASSES}
        return cls._LOCATORS

    @classmethod
    def make_parsing_context_id(cls) -> str:
        """
        Make random string that is the key for future local cache calls.
        """
        return str(random.uniform(0, 10000))

    @classmethod
    def clean_parsing_context(cls, context_id: Optional[str] = None) -> None:
        """
        The calling code cleans caches stored for this code by "context_id" key
        """
        if not context_id:
            return
        TermStemsCache.clean_local_cache(context_id, False)
        clean_geo_config_cache(context_id, False)
