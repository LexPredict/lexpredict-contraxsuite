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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import pickle
from typing import List, Dict
import pandas as pd
from django.utils.timezone import now

from apps.common.logger import CsLogger
from apps.common.models import ObjectStorage
from apps.common.singleton import Singleton


logger = CsLogger.get_django_logger()


class LocatingPerformanceRecord:
    def __init__(self, locator: str = '', duration: float = 0.0,
                 text_unit_id: int = 0, text_length: int = 0,
                 text_hash: int = 0):
        self.locator = locator
        self.duration = duration
        self.text_unit_id = text_unit_id
        self.text_length = text_length
        self.text_hash = text_hash

    @classmethod
    def get_text_hash(cls, text: str) -> int:
        return hash(text or '')

    def __repr__(self):
        return f'[{self.locator}]: {self.duration}s, {self.text_length}, ' +\
               f'#{self.text_unit_id}, hash: {self.text_hash}'


@Singleton
class LocatingPerformanceMeter:
    CACHE_KEY = 'LOCATING_PERFORMANCE'
    RECORDS_LIMIT = 20
    TOP_ABSOLUTE = 'absolute'
    TOP_RELATIVE = 'relative'

    def __init__(self):
        self.calls_add = 0
        self.calls_save = 0
        self.records_by_locator = {}  # type: Dict[str, List[LocatingPerformanceRecord]]
        self.init_collections()

    def init_collections(self):
        collections = self.load_collections()
        if collections:
            self.records_by_locator = collections

    def load_collections(self):
        collections = ObjectStorage.objects.filter(key=self.CACHE_KEY).first()
        if not collections:
            return None
        try:
            records = pickle.loads(collections.data)
            return records
        except Exception as e:
            logger.error(f'Error in LocatingPerformanceMeter.init_collections() (unpickle data): {e}')
        return None

    def clear_collections(self):
        ObjectStorage.objects.filter(key=self.CACHE_KEY).delete()

    def merge_collections(self,
                          stor_col: Dict[str, List[LocatingPerformanceRecord]],
                          new_col: Dict[str, List[LocatingPerformanceRecord]]) -> \
            Dict[str, List[LocatingPerformanceRecord]]:
        merged_col = {}  # type: Dict[str, List[LocatingPerformanceRecord]]
        keys = set(stor_col)
        keys.update(set(new_col))
        for key in keys:
            if key not in new_col:
                merged_col[key] = stor_col[key]
                continue
            if key not in stor_col:
                merged_col[key] = new_col[key]
                continue
            old_list = stor_col[key]
            new_list = new_col[key]
            merged_col[key] = self.merge_lists(old_list, new_list)
        return merged_col

    def merge_lists(self,
                    a_list: List[LocatingPerformanceRecord],
                    b_list: List[LocatingPerformanceRecord]) -> List[LocatingPerformanceRecord]:
        # merge by text_hash
        merged = []  # type: List[LocatingPerformanceRecord]
        b_by_hash = {b.text_hash: b for b in b_list}
        for a in a_list:
            counterpart = b_by_hash.get(a.text_hash)  # type: LocatingPerformanceRecord
            if counterpart:
                if counterpart.duration > a.duration:
                    merged.append(counterpart)
                else:
                    merged.append(a)
                del b_by_hash[a.text_hash]
            else:
                merged.append(a)
        for b_key in b_by_hash:
            merged.append(b_by_hash[b_key])
        merged.sort(key=lambda r: -r.duration)
        merged = merged[:self.RECORDS_LIMIT]
        return merged

    def store_collections(self):
        self.calls_save += 1
        records_to_store = self.records_by_locator
        stored = self.load_collections()
        # merge_collections
        if stored:
            records_to_store = self.merge_collections(records_to_store, stored)
        data = pickle.dumps(records_to_store)
        # compare data to store with data already stored
        try:
            ObjectStorage.objects.filter(key=self.CACHE_KEY).update_or_create(
                key=self.CACHE_KEY,
                defaults=dict(data=data, last_updated=now()))
        except Exception as e:
            logger.error(f'Error in LocatingPerformanceMeter.store_collections(): {e}')

    def to_mixed_dataframe(self, top_type: str, count: int = 30):
        # use ".to_dataframe()" to check then worst performers within each category:
        #  date, term, money etc.
        df = pd.DataFrame(columns=['Locator', 'Duration', 'Length', 'Text Unit'])

        top_records = []  # type: List[LocatingPerformanceRecord]
        for locator in self.records_by_locator:
            top_records += self.records_by_locator[locator]
        if top_type == self.TOP_ABSOLUTE:
            top_records.sort(key=lambda r: -r.duration)
        else:
            top_records.sort(key=lambda r: -r.duration / r.text_length)
        top_records = top_records[:count]

        for r in top_records:
            df = df.append({
                'Locator': r.locator,
                'Duration': r.duration,
                'Length': r.text_length,
                'Text Unit': r.text_unit_id,
            }, ignore_index=True)
        return df

    def add_record(self, locator: str, duration: float,
                   text_unit_id: int, text: str):
        if not duration or not text:
            return
        self.calls_add += 1
        records = self.records_by_locator.get(locator)
        if not records:
            self.records_by_locator[locator] = [LocatingPerformanceRecord(
                locator, duration, text_unit_id, len(text),
                LocatingPerformanceRecord.get_text_hash(text))]
            self.store_collections()
            return

        if len(records) >= self.RECORDS_LIMIT:
            min_time = records[-1].duration
            if duration <= min_time:
                return

        new_record = LocatingPerformanceRecord(
                locator, duration, text_unit_id, len(text),
                LocatingPerformanceRecord.get_text_hash(text))
        # add to the list or replace existing record
        same_worse_text_record, same_better_text_record = -1, -1
        for i, r in enumerate(records):
            if r.text_hash == new_record.text_hash:
                if r.duration < new_record.duration:
                    same_better_text_record = i
                    break
                same_worse_text_record = i
        if same_better_text_record >= 0:
            records[same_better_text_record] = new_record
        elif same_worse_text_record >= 0:
            return

        records.append(new_record)
        records.sort(key=lambda rd: -rd.duration)
        self.records_by_locator[locator] = records[:self.RECORDS_LIMIT]
        self.store_collections()
