import datetime
from collections import defaultdict
from typing import List, Set, Dict, Type, Optional

from django.db import transaction
from lexnlp.extract.en import (
    amounts, citations, copyright, courts, dates, distances, definitions,
    durations, geoentities, money, percents, ratios, regulations, trademarks, urls, dict_entities)
from lexnlp.extract.en.entities.nltk_maxent import get_companies
from lexnlp.nlp.en.tokens import get_stems, get_token_list

from apps.common.log_utils import ProcessLogger, render_error
from apps.document.models import TextUnitTag
from apps.extract import dict_data_cache
from apps.extract.models import (
    AmountUsage, CitationUsage, CopyrightUsage, CourtUsage, CurrencyUsage,
    DateDurationUsage, DateUsage, DefinitionUsage, DistanceUsage,
    GeoAliasUsage, GeoEntityUsage, PercentUsage, RatioUsage, RegulationUsage,
    Party, PartyUsage, TermUsage, TrademarkUsage, UrlUsage, Usage)


class ParseResults:
    __slots__ = ['usage_entities', 'text_unit_tags']

    def __init__(self, usage_entities: Dict[Type[Usage], List[Usage]],
                 text_unit_tags: Optional[Set[str]] = None) -> None:
        super().__init__()
        self.usage_entities = dict(
            usage_entities) if usage_entities is not None else dict()  # type: Dict[Type[Usage], List[Usage]]
        self.text_unit_tags = set(text_unit_tags) if text_unit_tags is not None else set()  # type: Set[str]


class LocationResults:
    def __init__(self) -> None:
        self.tags = defaultdict(set)  # type: Dict[int, Set[str]]
        self.located_usage_entities = defaultdict(list)  # type: Dict[Type[Usage], List]
        self.processed_usage_entity_classes = set()  # type: Set[Type[Usage]]
        self.processed_text_unit_ids = set()  # type: Set[int]

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
                    TextUnitTag.objects.filter(text_unit_id__in=self.processed_text_unit_ids).delete()
                    for entity_class in self.processed_usage_entity_classes:
                        entity_class.objects.filter(text_unit_id__in=self.processed_text_unit_ids).delete()

                count = 0
                for entity_class, entities in self.located_usage_entities.items():  # type: Type[Usage], List[Usage]
                    if entities:
                        entity_class.objects.bulk_create(entities, ignore_conflicts=True)
                        count += len(entities)

                tag_models = list()
                for text_unit_id, tags in self.tags.items():
                    for tag in tags:
                        tag_models.append(TextUnitTag(user_id=user_id,
                                                      text_unit_id=text_unit_id,
                                                      tag=tag))
                TextUnitTag.objects.bulk_create(tag_models, ignore_conflicts=True)
                log.info(
                    'Stored {0} usage entities and {1} tags for {2} text units'.format(
                        count, len(tag_models), len(self.processed_text_unit_ids)))
        except:
            msg = render_error(
                'Unable to store location results.\n'
                'Text unit ids: {text_unit_ids}\n'
                'Usage models caused the problem:\n{entities}'.format(
                    text_unit_ids=self.processed_text_unit_ids,
                    entities='\n'.join([str(e) for e in self.processed_usage_entity_classes])))
            log.error(msg)


class Locator:
    code = None

    locates_usage_model_classes = []

    def parse(self, text: str, text_unit_id: int, text_unit_lang: str, **kwargs) -> ParseResults:
        pass

    def try_parsing(self, log: ProcessLogger, locate_results: LocationResults, text: str,
                    text_unit_id: int, text_unit_lang: str, **kwargs):
        try:
            parse_results = self.parse(text, text_unit_id, text_unit_lang, **kwargs)  # type: ParseResults
            locate_results.collect(self, text_unit_id, parse_results)
        except:
            msg = render_error(
                'Exception caught while trying to run locator on a text unit.\n'
                'Locator: {locator}\n'
                'Text unit id: {text_unit_id}\n'
                'Text: {text}\n'
                'Text unit language: {text_unit_lang}\n'.format(
                    locator=self.__class__.__name__,
                    text_unit_id=text_unit_id,
                    text=text[:1024],
                    text_unit_lang=text_unit_lang))
            log.error(msg)


class AmountLocator(Locator):
    code = 'amount'

    locates_usage_model_classes = [AmountUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(amounts.get_amounts(text, return_sources=True, extended_sources=False))
        if found:
            unique = set(found)
            return ParseResults({AmountUsage: [AmountUsage(text_unit_id=text_unit_id,
                                                           amount=item[0],
                                                           amount_str=item[1][:300] if item[1] else None,
                                                           count=found.count(item)
                                                           ) for item in unique]})


class CitationLocator(Locator):
    code = 'citation'
    locates_usage_model_classes = [CitationUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(citations.get_citations(text, return_source=True))
        if found:
            unique = set(found)
            return ParseResults({CitationUsage: [CitationUsage(text_unit_id=text_unit_id,
                                                               volume=item[0],
                                                               reporter=item[1],
                                                               reporter_full_name=item[2],
                                                               page=item[3],
                                                               page2=item[4],
                                                               court=item[5],
                                                               year=item[6],
                                                               citation_str=item[7],
                                                               count=found.count(item)) for item in unique]})


class CourtLocator(Locator):
    code = 'court'

    locates_usage_model_classes = [CourtUsage]

    def parse(self, text, text_unit_id, text_unit_lang, **kwargs) -> ParseResults:
        court_config = dict_data_cache.get_court_config()
        found = [dict_entities.get_entity_id(i[0])
                 for i in courts.get_courts(text,
                                            court_config_list=court_config,
                                            text_languages=[text_unit_lang])]
        if found:
            unique = set(found)
            return ParseResults({CourtUsage: [CourtUsage(text_unit_id=text_unit_id,
                                                         court_id=court_id,
                                                         count=found.count(court_id)) for court_id in unique]})


class DistanceLocator(Locator):
    code = 'distance'

    locates_usage_model_classes = [DistanceUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(distances.get_distances(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({DistanceUsage: [DistanceUsage(text_unit_id=text_unit_id,
                                                               amount=item[0],
                                                               amount_str=item[2],
                                                               distance_type=item[1],
                                                               count=found.count(item)) for item in unique]})


class DateLocator(Locator):
    code = 'date'

    locates_usage_model_classes = [DateUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        strict = kwargs.get('strict', False)
        found = dates.get_dates_list(
            text,
            strict=strict,
            return_source=False)
        if found:
            unique = set([i.date() if isinstance(i, datetime.datetime) else i for i in found])
            return ParseResults({DateUsage: [DateUsage(text_unit_id=text_unit_id,
                                                       date=item,
                                                       count=found.count(item)) for item in unique]})


class DefinitionLocator(Locator):
    code = 'definition'

    locates_usage_model_classes = [DefinitionUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(definitions.get_definitions_in_sentence(text))
        if found:
            unique = set(found)
            return ParseResults({DefinitionUsage: [DefinitionUsage(text_unit_id=text_unit_id,
                                                                   definition=item,
                                                                   count=found.count(item)
                                                                   ) for item in unique]})


class DurationLocator(Locator):
    code = 'duration'

    locates_usage_model_classes = [DateDurationUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(durations.get_durations(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({DateDurationUsage: [DateDurationUsage(text_unit_id=text_unit_id,
                                                                       amount=item[1],
                                                                       amount_str=item[3],
                                                                       duration_type=item[0],
                                                                       duration_days=item[2],
                                                                       count=found.count(item)
                                                                       ) for item in unique]})


class CurrencyLocator(Locator):
    code = 'currency'

    locates_usage_model_classes = [CurrencyUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(money.get_money(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({CurrencyUsage: [CurrencyUsage(text_unit_id=text_unit_id,
                                                               amount=item[0],
                                                               amount_str=item[2],
                                                               currency=item[1],
                                                               count=found.count(item)
                                                               ) for item in unique]})


class PartyLocator(Locator):
    code = 'party'

    locates_usage_model_classes = [PartyUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(get_companies(text, count_unique=True, detail_type=True, name_upper=True))
        if found:
            pu_list = []
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
                    defaults=defaults
                )
                pu_list.append(
                    PartyUsage(text_unit_id=text_unit_id,
                               party=party,
                               count=count))
            return ParseResults({PartyUsage: pu_list})


class PercentLocator(Locator):
    code = 'percent'

    locates_usage_model_classes = [PercentUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(percents.get_percents(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({PercentUsage: [PercentUsage(text_unit_id=text_unit_id,
                                                             amount=item[1],
                                                             amount_str=item[3],
                                                             unit_type=item[0],
                                                             total=item[2],
                                                             count=found.count(item)) for item in unique]})


class RatioLocator(Locator):
    code = 'ratio'

    locates_usage_model_classes = [RatioUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(ratios.get_ratios(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({RatioUsage: [RatioUsage(text_unit_id=text_unit_id,
                                                         amount=item[0],
                                                         amount2=item[1],
                                                         amount_str=item[3],
                                                         total=item[2],
                                                         count=found.count(item)) for item in unique]})


class RegulationLocator(Locator):
    code = 'regulation'

    locates_usage_model_classes = [RegulationUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(regulations.get_regulations(text))
        if found:
            unique = set(found)
            return ParseResults({RegulationUsage: [RegulationUsage(text_unit_id=text_unit_id,
                                                                   regulation_type=item[0],
                                                                   regulation_name=item[1],
                                                                   count=found.count(item)) for item in unique]})


class CopyrightLocator(Locator):
    code = 'copyright'
    locates_usage_model_classes = [CopyrightUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(copyright.get_copyright(text, return_sources=True))
        if found:
            unique = set(found)
            return ParseResults({CopyrightUsage: [CopyrightUsage(text_unit_id=text_unit_id,
                                                                 year=item[1],
                                                                 name=item[2][:200],
                                                                 copyright_str=item[3][:200],
                                                                 count=found.count(item)
                                                                 ) for item in unique if len(item[2]) < 100]})


class TrademarkLocator(Locator):
    code = 'trademark'
    locates_usage_model_classes = [TrademarkUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(trademarks.get_trademarks(text))
        if found:
            unique = set(found)
            return ParseResults({TrademarkUsage: [TrademarkUsage(text_unit_id=text_unit_id,
                                                                 trademark=item,
                                                                 count=found.count(item)
                                                                 ) for item in unique]})


class UrlLocator(Locator):
    code = 'url'

    locates_usage_model_classes = [UrlUsage]

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        found = list(urls.get_urls(text))
        if found:
            unique = set(found)
            return ParseResults({UrlUsage: [UrlUsage(text_unit_id=text_unit_id,
                                                     source_url=item,
                                                     count=found.count(item)) for item in unique]})


class GeoEntityLocator(Locator):
    code = 'geoentity'

    locates_usage_model_classes = [GeoEntityUsage, GeoAliasUsage]

    def parse(self, text, text_unit_id, text_unit_lang, **kwargs) -> ParseResults:
        priority = kwargs.get('priority', True)
        geo_config = dict_data_cache.get_geo_config()
        entity_alias_pairs = list(geoentities.get_geoentities(text,
                                                              geo_config,
                                                              text_languages=[text_unit_lang],
                                                              priority=priority))

        entity_ids = [dict_entities.get_entity_id(entity) for entity, _alias in entity_alias_pairs]
        if entity_ids:
            unique_entities = set(entity_ids)
            alias_ids = [dict_entities.get_alias_id(alias) for _entity, alias in entity_alias_pairs]
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

    def parse(self, text, text_unit_id, _text_unit_lang, **kwargs) -> ParseResults:
        term_stems = dict_data_cache.get_term_config()
        text_stems = ' %s ' % ' '.join(get_stems(text, lowercase=True))
        text_tokens = get_token_list(text, lowercase=True)
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


LOCATOR_CLASSES = [AmountLocator, CitationLocator, CopyrightLocator, CourtLocator, CurrencyLocator,
                   DurationLocator, DateLocator, DefinitionLocator, DistanceLocator, GeoEntityLocator,
                   PercentLocator, RatioLocator, RegulationLocator, PartyLocator, TermLocator, TrademarkLocator,
                   UrlLocator]

LOCATORS = {locator_class.code: locator_class() for locator_class in LOCATOR_CLASSES}  # type: Dict[str, Locator]
