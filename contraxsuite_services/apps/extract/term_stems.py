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

from typing import List, Set, Dict, Union, Optional

from lexnlp.nlp.en.tokens import get_stems

from apps.common import redis
from apps.common.utils import GroupConcat
from apps.extract.models import Term, TermTag
from apps.project.models import Project

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TermStemsCacheRecord:
    def __init__(self,
                 term: str,
                 stemmed: str,
                 pk: int,
                 tags: Set[str]):
        self.term = term
        self.stemmed = stemmed
        self.pk = pk
        self.tags = tags or ''

    def __str__(self):
        tags_str = ', '.join(self.tags)
        return f'"{self.term}" (#{self.pk}), stemmed: "{self.stemmed}", tags: {tags_str}'


class TermStemsCache:
    CACHE_KEY_TERM_STEMS = 'term_stems'

    # This cache is to be controlled by the process (celery task) that runs methods that detect terms.
    # The cache should be cleaned upon the parent process completion.
    # An example of the parent task is "parse_text_units" function.
    # key: parent context "id", probably a random floating point value or UUID
    # value: Dict[<project id>: <get_term_stems() ret value>]
    LOCAL_CACHE: Dict[str, Dict[int, Dict[str, Dict[str, Union[List[List[Union[str, int]]], int]]]]] = {}

    @classmethod
    def invalidate(cls):
        redis.push(TermStemsCache.CACHE_KEY_TERM_STEMS, None)

    @classmethod
    def clean_local_cache(cls, context_id: str, clean_all: bool):
        if clean_all:
            cls.LOCAL_CACHE = {}
        else:
            if context_id in cls.LOCAL_CACHE:
                del cls.LOCAL_CACHE[context_id]

    # Redis cache for term stems
    @classmethod
    def cache(cls) -> List[TermStemsCacheRecord]:
        terms_to_cache: List[TermStemsCacheRecord] = []
        terms_qs = Term.objects.annotate(tag_names=GroupConcat('tags__name')).values_list('term', 'pk', 'tag_names')

        for t, pk, tags in terms_qs:
            stemmed_term: str = ' %s ' % ' '.join(get_stems(t))
            tag_list = {t.strip() for t in (tags or '').split(',')}
            record = TermStemsCacheRecord(t, stemmed_term, pk, tag_list)
            terms_to_cache.append(record)
        redis.push(TermStemsCache.CACHE_KEY_TERM_STEMS, terms_to_cache)
        return terms_to_cache

    @classmethod
    def get_term_stems(cls,
                       project_id: int,
                       parsing_context_id: Optional[str] = None,
                       selected_tags: Optional[List[str]] = None) \
            -> Dict[str, Dict[str, Union[List[List[Union[str, int]]], int]]]:
        """
        Reads terms (with tags and stems) from cache, filters terms by tags
        :param project_id:
        :return: {' 401 ( k ) plan ': {'values': [['401(k) plan', 1]], 'length': 1}, ... }
        """
        if parsing_context_id:
            if parsing_context_id not in cls.LOCAL_CACHE:
                cls.LOCAL_CACHE[parsing_context_id] = {}
            cached_project_stems = cls.LOCAL_CACHE[parsing_context_id].get(project_id)
            if cached_project_stems:
                return cached_project_stems

        project = Project.all_objects.get(pk=project_id)
        if selected_tags:
            project_tags = set(selected_tags)
        else:
            project_tags = set(project.term_tags.values_list('name', flat=True)) or {TermTag.DEFAULT_TAG}
        cached: List[TermStemsCacheRecord] = redis.pop(TermStemsCache.CACHE_KEY_TERM_STEMS)
        if not cached:
            cached = cls.cache()
        if not cached:
            return {}

        # NB: these lines (up to return) takes ~ 90% of the method execution time
        project_terms = [c for c in cached if c.tags.intersection(project_tags)]
        term_stems: Dict[str, Dict[str, Union[List[List[Union[str, int]]], int]]] = {}
        for record in project_terms:
            if record.stemmed in term_stems:
                term_stems[record.stemmed]['values'].append([record.term, record.pk])
                term_stems[record.stemmed]['length'] = term_stems[record.stemmed]['length'] + 1
            else:
                term_stems[record.stemmed] = {
                    'values': [[record.term, record.pk]],
                    'length': 1
                }
        if parsing_context_id:
            cls.LOCAL_CACHE[parsing_context_id][project_id] = term_stems

        return term_stems
