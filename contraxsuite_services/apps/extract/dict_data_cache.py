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

import logging
from typing import Dict, List, Optional

from lexnlp.extract.en import dict_entities
from lexnlp.extract.en.dict_entities import DictionaryEntry

from apps.common import redis
from apps.extract.models import GeoEntity, GeoAlias, Court

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


CACHE_KEY_GEO_CONFIG = 'geo_config'
CACHE_KEY_COURT_CONFIG = 'court_config'
CACHE_KEY_PARTY_CONFIG = 'party_config'


# local cache for geo-entity configuration
# key: "cache context" id
# value: the same data we store in redis[CACHE_KEY_GEO_CONFIG]
LOCAL_GEO_CONFIG: Dict[str, List[DictionaryEntry]] = {}


def cache_geo_config():
    geo_config = {}
    for name, pk, priority in GeoEntity.objects.values_list('name', 'pk', 'priority'):
        entity = dict_entities.DictionaryEntry(pk, name, priority or 0, name_is_alias=True)
        geo_config[pk] = entity
    for alias_id, alias_text, alias_type, entity_id, alias_lang \
            in GeoAlias.objects.values_list('pk', 'alias', 'type', 'entity', 'locale'):
        entity = geo_config[entity_id]
        if entity:
            is_abbrev = alias_type.startswith('iso') or alias_type.startswith('abbrev')
            for alias in alias_text.split(';'):
                entity.aliases.append(dict_entities.DictionaryEntryAlias(
                    alias, language=alias_lang, is_abbreviation=is_abbrev, alias_id=alias_id
                ))
    res = list(geo_config.values())

    # DbCache.put_to_db(CACHE_KEY_GEO_CONFIG, res)
    redis.push(CACHE_KEY_GEO_CONFIG, res)
    return res


def clean_geo_config_cache(cache_context_id: Optional[str] = None, clean_all: bool = False):
    global LOCAL_GEO_CONFIG
    if clean_all:
        LOCAL_GEO_CONFIG = {}
        return
    if cache_context_id in LOCAL_GEO_CONFIG:
        del LOCAL_GEO_CONFIG[cache_context_id]


def get_geo_config(cache_context_id: Optional[str] = None):
    if cache_context_id:
        if cache_context_id in LOCAL_GEO_CONFIG:
            return LOCAL_GEO_CONFIG[cache_context_id]

    config = redis.pop(CACHE_KEY_GEO_CONFIG)
    if config:
        if cache_context_id:
            LOCAL_GEO_CONFIG[cache_context_id] = config
        return config
    # either it doesn't exist OR it's empty
    config = cache_geo_config()
    if cache_context_id:
        LOCAL_GEO_CONFIG[cache_context_id] = config
    return config


def cache_court_config():
    res = [dict_entities.DictionaryEntry(
           id=i.id,
           name=i.name,
           priority=0,
           aliases=[dict_entities.DictionaryEntryAlias(a) for a in i.alias.split(';')] if i.alias else []
    ) for i in Court.objects.all()]

    # DbCache.put_to_db(CACHE_KEY_COURT_CONFIG, res)
    redis.push(CACHE_KEY_COURT_CONFIG, res)
    return res


def get_court_config():
    # return DbCache.get(CACHE_KEY_COURT_CONFIG)

    config = redis.pop(CACHE_KEY_COURT_CONFIG)
    if config:
        return config
    # either it doesn't exist OR it's empty
    return cache_court_config()


# def cache_party_config():
#     redis.r.delete(CACHE_KEY_PARTY_CONFIG)
#     qs = Party.objects \
#         .annotate(uniq=Concat(F('type_abbr'), Value(':'), F('name'))) \
#         .values_list('uniq', 'id')
#     cached_data = {k: v for k, v in qs}
#     redis.r.hmset(CACHE_KEY_PARTY_CONFIG, cached_data)
#     return cached_data
#
#
# def get_party_config():
#     config = redis.r.hgetall(CACHE_KEY_PARTY_CONFIG)
#     if config:
#         return {k.decode('utf-8'): v.decode('utf-8') for k, v in config.items()}
#     return cache_party_config()


def init_config_cache():
    """
    Cache configs on app start
    """
    logging.info('Initiate cache for configs')

    cache_geo_config()
    print('Cached Geo config')

    cache_court_config()
    print('Cached Courts config')

    # cache_party_config()
    # print('Cached Parties config')
