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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
from typing import List, Set, Optional
from lexnlp.config.en.company_types import COMPANY_TYPES, COMPANY_DESCRIPTIONS
from lexnlp.extract.en.entities.company_detector import CompanyDetector

from apps.common import redis
from apps.common.utils import GroupConcat
from apps.extract.models import CompanyType, CompanyTypeTag
from apps.project.models import Project


class CompanyTypeCacheRecord:
    def __init__(self,
                 alias: str,
                 abbreviation: str,
                 label: str,
                 pk: int,
                 tags: Set[str]):
        self.alias = alias
        self.abbreviation = abbreviation
        self.label = label
        self.pk = pk
        self.tags = tags or ''

    def __str__(self):
        tags_str = ', '.join(self.tags)
        return f'"{self.abbreviation}", "{self.alias}" (#{self.pk}), label: "{self.label}", tags: {tags_str}'


class CompanyTypeCache:
    CACHE_KEY_COMPANY_TYPES = 'company_types'

    cached_detector: Optional[CompanyDetector] = None

    # this hash is build on all CompanyType records collected for the particular project
    # if the cache is the same as it was in the last function call, we use cached_detector
    # (of course, if cached_detector is not None)
    cached_comp_type_hash = ''

    # we may not even check cached_comp_type_hash if cached_detector was cached
    # for a short period of time for the same cached_project_id
    cached_project_id = 0

    cached_project_time: Optional[datetime.datetime] = None

    CACHE_INTERVAL_SECONDS = 4.0

    @classmethod
    def invalidate(cls):
        redis.push(CompanyTypeCache.CACHE_KEY_COMPANY_TYPES, None)

    # Redis cache for company types
    @classmethod
    def cache(cls) -> List[CompanyTypeCacheRecord]:
        records_to_cache: List[CompanyTypeCacheRecord] = []
        qs = CompanyType.objects.annotate(
            tag_names=GroupConcat('tags__name')).values_list(
            'alias', 'abbreviation', 'label', 'pk', 'tag_names')

        for alias, abbr, label, pk, tags in qs:
            tag_list = {t.strip() for t in (tags or '').split(',')}
            record = CompanyTypeCacheRecord(alias, abbr, label, pk, tag_list)
            records_to_cache.append(record)
        redis.push(CompanyTypeCache.CACHE_KEY_COMPANY_TYPES, records_to_cache)
        return records_to_cache

    @classmethod
    def get_company_types(cls,
                          project_id: Optional[int],
                          selected_tags: Optional[List[str]]) -> List[CompanyType]:
        """
        Reads company types from cache, filters types by tags
        :return: List[CompanyType]
        """
        cached: List[CompanyTypeCacheRecord] = redis.pop(CompanyTypeCache.CACHE_KEY_COMPANY_TYPES)
        if not cached:
            cached = cls.cache()
        if not cached:
            return []
        if selected_tags:
            project_tags = set(selected_tags)
        elif project_id:
            project = Project.all_objects.get(pk=project_id)
            project_tags = set(project.companytype_tags.values_list('name', flat=True)) \
                           or {CompanyTypeTag.DEFAULT_TAG}
        else:
            project_tags = {CompanyTypeTag.DEFAULT_TAG}
        project_comp_types = [c for c in cached if c.tags.intersection(project_tags)]

        return [CompanyType(alias=c.alias, abbreviation=c.abbreviation, label=c.label)
                for c in project_comp_types]

    @classmethod
    def get_company_detector(cls,
                             project_id: Optional[int],
                             selected_tags: Optional[List[str]]) -> CompanyDetector:
        if cls.cached_project_id == project_id and cls.cached_project_time:
            time_since_cached = (datetime.datetime.now() - cls.cached_project_time).total_seconds()
            if time_since_cached < cls.CACHE_INTERVAL_SECONDS:
                return cls.cached_detector
        cls.cached_project_id = project_id

        comp_types = cls.get_company_types(project_id, selected_tags)
        comp_types_hash = CompanyType.get_comp_types_hash(comp_types)
        if cls.cached_detector and cls.cached_comp_type_hash == comp_types_hash:
            cls.cached_project_time = datetime.datetime.now()
            return cls.cached_detector

        comp_dict = CompanyType.to_company_descriptors(comp_types) if comp_types else COMPANY_TYPES
        company_detector = CompanyDetector(comp_dict, COMPANY_DESCRIPTIONS)
        cls.cached_detector = company_detector
        cls.cached_comp_type_hash = comp_types_hash
        cls.cached_project_time = datetime.datetime.now()
        return company_detector
