import threading
import time
from datetime import datetime

from lexnlp.extract.en import dict_entities
from lexnlp.nlp.en.tokens import get_stems

from apps.common.models import ObjectStorage
from apps.extract.models import GeoEntity, GeoAlias, Court, Term

CACHE_KEY_GEO_CONFIG = 'geo_config'
CACHE_KEY_COURT_CONFIG = 'court_config'
CACHE_KEY_TERM_STEMS = 'term_stems'


class DbCache:
    CACHE_IN_MEMORY_REFRESH_SECONDS = 20

    INSTANCE = None

    lock = threading.RLock()

    def __init__(self) -> None:
        super().__init__()
        self.in_memory_cache = {}
        self.watch_thread = threading.Thread(target=self._check_cache)
        self._stop_watcher = False
        self.watch_thread.start()

    def stop_watching(self):
        self._stop_watcher = True

    def _check_cache(self):
        while self.watch_thread.is_alive() and not self._stop_watcher:
            time.sleep(self.CACHE_IN_MEMORY_REFRESH_SECONDS)
            self.lock.acquire()
            try:
                for key in set(self.in_memory_cache.keys()):
                    last_update_date, value = self.in_memory_cache[key]
                    if (datetime.now() - last_update_date).seconds \
                            > self.CACHE_IN_MEMORY_REFRESH_SECONDS:
                        del self.in_memory_cache[key]

            finally:
                self.lock.release()

    @staticmethod
    def load_from_db(key: str):
        try:
            return ObjectStorage.objects.get(key=key).get_obj()
        except ObjectStorage.DoesNotExist:
            return None

    @staticmethod
    def put_to_db(key: str, value):
        ObjectStorage.update_or_create(key, value)

    def _get(self, key: str):
        self.lock.acquire()
        try:
            record = self.in_memory_cache.get(key)

            if not record or (datetime.now() - record[0]).seconds \
                    > DbCache.CACHE_IN_MEMORY_REFRESH_SECONDS:
                record = (datetime.now(), self.load_from_db(key))
                self.in_memory_cache[key] = record

            return record[1]
        finally:
            self.lock.release()

    @staticmethod
    def get(key: str):
        DbCache.lock.acquire()
        try:
            if DbCache.INSTANCE is None:
                DbCache.INSTANCE = DbCache()
            return DbCache.INSTANCE._get(key)
        finally:
            DbCache.lock.release()

    @staticmethod
    def cache_geo_config(*args, **kwargs) -> None:
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

    @classmethod
    def get_geo_config(cls):
        return DbCache.get(CACHE_KEY_GEO_CONFIG)

    @staticmethod
    def cache_court_config(*args, **kwargs):
        res = [dict_entities.entity_config(
            entity_id=i.id,
            name=i.name,
            priority=0,
            aliases=i.alias.split(';') if i.alias else []
        ) for i in Court.objects.all()]
        DbCache.put_to_db(CACHE_KEY_COURT_CONFIG, res)

    @classmethod
    def get_court_config(cls):
        return DbCache.get(CACHE_KEY_COURT_CONFIG)

    @staticmethod
    def cache_term_stems(*args, **kwargs):
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

    @classmethod
    def get_term_config(cls):
        return DbCache.get(CACHE_KEY_TERM_STEMS)
