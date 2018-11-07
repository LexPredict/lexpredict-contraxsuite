from lexnlp.extract.en import dict_entities
from lexnlp.nlp.en.tokens import get_stems

from apps.common.advancedcelery.db_cache import DbCache
from apps.extract.models import GeoEntity, GeoAlias, Court, Term

CACHE_KEY_GEO_CONFIG = 'geo_config'
CACHE_KEY_COURT_CONFIG = 'court_config'
CACHE_KEY_TERM_STEMS = 'term_stems'


def cache_geo_config():
    geo_config = {}
    for name, pk, priority in GeoEntity.objects.values_list('name', 'pk', 'priority'):
        entity = dict_entities.entity_config(pk, name, priority or 0, name_is_alias=True)
        geo_config[pk] = entity
    for alias_id, alias_text, alias_type, entity_id, alias_lang \
            in GeoAlias.objects.values_list('pk', 'alias', 'type', 'entity', 'locale'):
        entity = geo_config[entity_id]
        if entity:
            is_abbrev = alias_type.startswith('iso') or alias_type.startswith('abbrev')
            dict_entities.add_aliases_to_entity(entity,
                                                aliases_csv=alias_text,
                                                language=alias_lang,
                                                is_abbreviation=is_abbrev,
                                                alias_id=alias_id)
    res = list(geo_config.values())
    DbCache.put_to_db(CACHE_KEY_GEO_CONFIG, res)


def get_geo_config():
    return DbCache.get(CACHE_KEY_GEO_CONFIG)


def cache_court_config():
    res = [dict_entities.entity_config(
        entity_id=i.id,
        name=i.name,
        priority=0,
        aliases=i.alias.split(';') if i.alias else []
    ) for i in Court.objects.all()]
    DbCache.put_to_db(CACHE_KEY_COURT_CONFIG, res)


def get_court_config():
    return DbCache.get(CACHE_KEY_COURT_CONFIG)


def cache_term_stems():
    term_stems = {}
    for t, pk in Term.objects.values_list('term', 'pk'):
        stemmed_term = ' %s ' % ' '.join(get_stems(t))
        stemmed_item = term_stems.get(stemmed_term, [])
        stemmed_item.append([t, pk])
        term_stems[stemmed_term] = stemmed_item
    for item in term_stems:
        term_stems[item] = dict(values=term_stems[item],
                                length=len(term_stems[item]))
    DbCache.put_to_db(CACHE_KEY_TERM_STEMS, term_stems)


def get_term_config():
    return DbCache.get(CACHE_KEY_TERM_STEMS)
