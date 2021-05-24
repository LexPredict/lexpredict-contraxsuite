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

# Standard imports
import pandas as pd
from pandas import DataFrame, Series
from typing import Callable, Tuple, List, Optional, Dict, Any

# Project imports
import settings
from apps.common.utils import GroupConcat
from apps.extract.models import GeoEntity, GeoAlias, Term, Court, TermTag

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: parse github repo?
# f.e.: https://api.github.com/repos/LexPredict/lexpredict-legal-dictionary/contents/en
DEFAULT_DICTIONARY_DATA_URL_MAP = dict(
    terms_accounting_4='accounting/us_gaap.csv',
    terms_financial_1='financial/financial.csv',
    terms_legal_4='legal/common_US_terms_top1000.csv',
    terms_legal_5='legal/common_top_law_terms.csv',
    courts_1='legal/ca_courts.csv',
    courts_2='legal/us_courts.csv',
    geoentities_1='geopolitical/geopolitical_divisions.csv',
)

DICTIONARY_DATA_URL_MAP = dict(
    terms_accounting_1='accounting/ifrs_iasb.csv',
    terms_accounting_2='accounting/uk_gaap.csv',
    terms_accounting_3='accounting/us_fasb.csv',
    terms_accounting_4='accounting/us_gaap.csv',
    terms_accounting_5='accounting/us_gasb.csv',
    terms_financial_1='financial/financial.csv',
    terms_legal_1='legal/common_law.csv',
    terms_legal_2='legal/us_cfr.csv',
    terms_legal_3='legal/us_usc.csv',
    terms_legal_4='legal/common_US_terms_top1000.csv',
    terms_legal_5='legal/common_top_law_terms.csv',
    terms_scientific_1='scientific/us_hazardous_waste.csv',
    courts_1='legal/ca_courts.csv',
    courts_2='legal/us_courts.csv',
    geoentities_1='geopolitical/geopolitical_divisions.csv',
)

LOCALES_MAP = (
    ('German Name', 'de', 'German Name'),
    ('Spanish Name', 'es', 'Spanish Name'),
    ('French Name', 'fr', 'French Name'),
    ('ISO-3166-2', 'en', 'iso-3166-2'),
    ('ISO-3166-3', 'en', 'iso-3166-3'),
    ('Alias', 'en', 'abbreviation'),
)


def fake_progress() -> None:
    return None


def load_geo_entities(df: DataFrame, total_progress: Callable[[int], None] = None,
                      progress: Callable = None) -> Tuple[int, int]:
    # create Geo Entities
    geo_aliases = []
    geo_entities_count = 0

    if not progress:
        progress = fake_progress

    if total_progress:
        total_progress(len(df) + 1)

    df = df.drop_duplicates().fillna('')
    for _, row in df.iterrows():
        latitude, longitude = None, None
        entity_id = row['Entity ID']
        entity_name = row['Entity Name'].strip()
        entity_priority = row.get('Entity Priority')
        if entity_priority:
            try:
                entity_priority = int(entity_priority)
            except ValueError:
                entity_priority = 0
        else:
            entity_priority = 0

        if 'Latitude' in row and row['Latitude']:
            latitude = row['Latitude']
            longitude = row['Longitude']

        the_entity = GeoEntity.objects.filter(entity_id=entity_id)
        if the_entity.exists:
            the_entity.delete()

        entity = GeoEntity.objects.create(
            entity_id=entity_id,
            name=entity_name,
            priority=entity_priority,
            category=row['Entity Category'].strip(),
            latitude=latitude,
            longitude=longitude)
        geo_entities_count += 1

        for column_name, locale, alias_type in LOCALES_MAP:
            if not row[column_name]:
                continue
            geo_aliases.append(
                GeoAlias(
                    entity=entity,
                    locale=locale,
                    alias=row[column_name],
                    type=alias_type))
        progress()

    GeoAlias.objects.bulk_create(geo_aliases)
    progress()

    return len(geo_aliases), geo_entities_count


def load_terms(df: DataFrame,
               existing_action: str = 'update',
               tags: Optional[List[str]] = None) -> int:
    """Creates Term objects from an input Pandas DataFrame and adds the newly created Terms to the database.

    Args:
        df (pandas.DataFrame): Input data. Contains columns:

            * 'Locale'
            * 'Source'
            * 'Term'
            * ['Tags'] - optional column
            * ['Case Sensitive'] - optional column

        existing_action (str): A logical flag for handling duplicate Term conflicts.
            Can be 'add', 'ignore', or 'replace'. Defaults to 'ignore'.
            Only relevant if a Term already exists in the database.

            * 'delete': delete terms and add those we read from the file
            * 'skip': skips the Term if it's already in the DB
            * 'update': deletes the old Term(s) and then adds the new Term.

        :param tags: Optional list of term tags to use when no tags are provided
             in the source dataframe.

    Returns:
        int: The number of Terms added / updated to the database.

    Raises:
        ValueError: invalid `term_creation_mode` argument.
    """
    # preprocess DataFrame
    df.drop_duplicates(inplace=True)
    if 'Case Sensitive' in df:
        df.loc[df['Case Sensitive'].eq(False), 'Term'] = df.loc[
            df['Case Sensitive'].eq(False), 'Term'].str.lower()
        df = df.drop_duplicates(subset='Term').dropna(subset=['Term'])

    # create new Terms. Filter: if _prepare_term() returns None, it is not added to this list
    if tags:
        tags = sorted(tags)
    if existing_action == 'delete':
        Term.objects.all().delete()

    existing_terms = {t.term: t for t in Term.objects.annotate(tag_list=GroupConcat('tags__name'))}
    tag_by_name = {t.name: t for t in TermTag.objects.all()}

    count_updated = 0
    for _, row in df.iterrows():
        if 'Tags' not in row:
            new_term_tags = tags
        else:
            tags_from_file = sorted(t.strip() for t in row.get('Tags', '').split(','))
            new_term_tags = tags_from_file if tags_from_file else tags

        term_data = deserialize_term_from_row(
            row, existing_terms, new_term_tags, existing_action)
        if not term_data:
            continue
        count_updated += 1

        term, new_item = Term.objects.get_or_create(
            term=term_data['term'], defaults=term_data)

        if not new_item and term.tags is not None:
            # remove tags that are no more associated with the term
            extra_tags = [t for t in term.tags.all() if t.name not in new_term_tags]
            for tag in extra_tags:
                term.tags.remove(tag)

        for tag in new_term_tags:
            tag_obj = tag_by_name.get(tag)
            if not tag_obj:
                tag_obj = TermTag()
                tag_obj.name = tag
                tag_obj.save()
            term.tags.add(tag_obj)
        term.save()
    # TODO: CS-4577: cache "global" term stems step - should be cached here via model manager ?

    return count_updated


def deserialize_term_from_row(
        dataframe_row: Series,
        existing_terms: Dict[str, Term],
        new_term_tags: List[str],
        on_exists: str) -> Optional[Dict[str, Any]]:
    term = dataframe_row['Term'].strip()
    existing_term = existing_terms.get(term)
    if existing_term and on_exists == 'skip':
        return None
    # instantiate a new term prop dictionary
    new_db_term = {
        'term': term,
        'source': dataframe_row.get('Source', dataframe_row.get('Term Category')),
        'definition_url': dataframe_row.get('Locale', dataframe_row.get('Term Locale'))
    }

    # check the term differs from the one we stored
    is_updated = existing_term is None
    if not is_updated:
        for key in new_db_term:
            if new_db_term[key] != getattr(existing_term, key):
                is_updated = True
                break
        if not is_updated:  # check referenced TermTags
            ex_tags = sorted([t.strip() for t in existing_term.tag_list.split(',')])
            is_updated = ex_tags != new_term_tags

    if not is_updated:
        return None
    return new_db_term


def load_courts(df: DataFrame) -> int:
    df = df.dropna(subset=['Court ID']).fillna('')
    df['Court ID'] = df['Court ID'].astype(int)

    courts_dst = []
    for _, row in df.iterrows():
        if not Court.objects.filter(
                court_id=row['Court ID'],
                alias=row['Alias']).exists():
            court = Court(
                court_id=row['Court ID'],
                type=row['Court Type'],
                name=row['Court Name'],
                level=row['Level'],
                jurisdiction=row['Jurisdiction'],
                alias=row['Alias']
            )
            courts_dst.append(court)
    Court.objects.bulk_create(courts_dst)
    return len(df)


def get_dictionary_data_urls(dictionary_name: str, locale: str, use_default_url_map=True) -> list:
    result = []
    url_map = DEFAULT_DICTIONARY_DATA_URL_MAP if use_default_url_map else DICTIONARY_DATA_URL_MAP
    for key, url in url_map.items():
        if key.startswith(dictionary_name):
            url = '{0}/{1}/{2}'.format(settings.GIT_DATA_REPO_ROOT, locale, url)
            result.append(url)
    return result


def get_terms_data_urls(locale='en', use_default_url_map=True) -> list:
    return get_dictionary_data_urls('terms', locale, use_default_url_map)


def get_courts_data_urls(locale='en', use_default_url_map=True) -> list:
    return get_dictionary_data_urls('courts', locale, use_default_url_map)


def get_geoentities_data_urls(locale='multi', use_default_url_map=True) -> list:
    return get_dictionary_data_urls('geoentities', locale, use_default_url_map)


def load_df(urls: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for url in urls:
        df = df.append(pd.read_csv(url))
    return df
