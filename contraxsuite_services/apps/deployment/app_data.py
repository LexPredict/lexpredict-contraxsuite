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
from pandas import DataFrame
from typing import Callable, Tuple

# Project imports
import settings
from apps.extract.models import GeoEntity, GeoAlias, Term, Court

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.1.9"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# TODO: parse github repo?
# f.e.: https://api.github.com/repos/LexPredict/lexpredict-legal-dictionary/contents/en
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


def load_terms(df: DataFrame) -> int:
    df.drop_duplicates(inplace=True)
    df.loc[df["Case Sensitive"] == False, "Term"] = df.loc[
        df["Case Sensitive"] == False, "Term"].str.lower()
    df = df.drop_duplicates(subset="Term").dropna(subset=["Term"])

    terms = []
    for row_id, row in df.iterrows():
        term = row["Term"].strip()
        if not Term.objects.filter(term=term).exists():
            lt = Term()
            lt.term = term
            lt.source = row["Term Category"]
            lt.definition_url = row["Term Locale"]
            terms.append(lt)

    Term.objects.bulk_create(terms)
    return len(df)


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


def get_dictionary_data_urls(dictionary_name: str, locale: str) -> list:
    result = []
    for key, url in DICTIONARY_DATA_URL_MAP.items():
        if key.startswith(dictionary_name):
            url = '{0}/{1}/{2}'.format(settings.GIT_DATA_REPO_ROOT, locale, url)
            result.append(url)
    return result


def get_terms_data_urls(locale='en') -> list:
    return get_dictionary_data_urls('terms', locale)


def get_courts_data_urls(locale='en') -> list:
    return get_dictionary_data_urls('courts', locale)


def get_geoentities_data_urls(locale='multi') -> list:
    return get_dictionary_data_urls('geoentities', locale)


def load_df(urls: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for url in urls:
        df = df.append(pd.read_csv(url))
    return df
