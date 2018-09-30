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

# Django imports
import geocoder
from pandas import DataFrame
from typing import Callable, Tuple
from apps.extract.models import GeoEntity, GeoAlias, Term, Court

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

        if 'latitude' in row and row['latitude']:
            latitude = row['latitude']
            longitude = row['longitude']
        else:
            g = geocoder.google(entity_name)
            if not g.latlng and ',' in entity_name:
                g = geocoder.google(entity_name.split(',')[0])
            latitude, longitude = g.latlng if g.latlng else (None, None)

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

