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

import pandas as pd
from IPython.display import display
from typing import List

from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.common.models import MethodStatsCollectorPlugin, MethodStats

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ModelStatsSetsManager:
    """
    ModelStatsSetsManager helps with turning on / off methods' logging
    for a bunch of methods.
    Usage example:
    from apps.common.model_utils.model_stats_sets_manager import ModelStatsSetsManager
    ModelStatsSetsManager.remove_all_decorators()
    ModelStatsSetsManager.decorate_all_standard_methods()
    ModelStatsSetsManager.purge_stored_statistics()
    """
    deprecated_methods = {'lock_document'}

    @staticmethod
    def get_class_methods(cls_obj) -> List[str]:
        methods = [func for func in dir(cls_obj)
                   if callable(getattr(cls_obj, func))
                   and not func.startswith('_')
                   and func not in ModelStatsSetsManager.deprecated_methods]
        return methods

    @staticmethod
    def get_docfieldrepo_methods() -> List[str]:
        path = 'apps.document.repository.document_field_repository.DocumentFieldRepository.'
        repo = DocumentFieldRepository()
        return [path + m for m in ModelStatsSetsManager.get_class_methods(repo)]

    @staticmethod
    def get_fields_detecting_methods() -> List[str]:
        funcs = ['apps.document.field_detection.field_detection.' +
                 'detect_and_cache_field_values_for_document']
        return funcs

    @staticmethod
    def get_field_locators() -> List[str]:
        path = 'apps.document.field_detection.regexps_and_text_based_ml_field_detection'
        cls = ['RegexpsAndTextBasedMLFieldDetectionStrategy', 'TextBasedMLFieldDetectionStrategy']
        methods = [f'{path}.{c}.detect_field_value' for c in cls]

        path = 'apps.document.field_detection.regexps_field_detection'
        cls = ['RegexpsOnlyFieldDetectionStrategy', 'FieldBasedRegexpsDetectionStrategy']
        methods += [f'{path}.{c}.detect_field_value' for c in cls]

        path = 'apps.document.field_detection.csv_regexps_field_detection_strategy'
        cls = ['CsvRegexpsFieldDetectionStrategy']
        methods += [f'{path}.{c}.detect_field_value' for c in cls]
        return methods

    @staticmethod
    def get_common_locators() -> List[str]:
        path = 'apps.extract.locators'
        cls = ['AmountLocator', 'CitationLocator', 'CourtLocator', 'DistanceLocator',
               'DateLocator', 'DefinitionLocator', 'DurationLocator', 'CurrencyLocator',
               'PartyLocator', 'PercentLocator', 'RatioLocator', 'RegulationLocator',
               'CopyrightLocator', 'TrademarkLocator', 'UrlLocator', 'GeoEntityLocator', 'TermLocator']
        methods = [f'{path}.{c}.parse' for c in cls]
        return methods

    @staticmethod
    def decorate_methods(methods: List[str],
                         active: bool = True, log_sql: bool = False):
        decorators = []
        for met in methods:
            met_name = met.split('.')[-1]
            dc = MethodStatsCollectorPlugin(path=met, name=met_name, log_sql=log_sql)
            decorators.append(dc)
        MethodStatsCollectorPlugin.objects.bulk_create(decorators, ignore_conflicts=True)
        print(f'Created {len(decorators)} decorators')

    @staticmethod
    def remove_all_decorators():
        count = MethodStatsCollectorPlugin.objects.all().count()
        MethodStatsCollectorPlugin.objects.all().delete()
        print(f'Deleted {count} decorators')

    @staticmethod
    def show_stored_decorators():
        df = pd.DataFrame(columns=['Path', 'Name', 'Log SQL'])
        for sets in MethodStatsCollectorPlugin.objects.all():
            df = df.append({
                "Path": sets.path,
                "Name": sets.name,
                "Log SQL": sets.log_sql
            }, ignore_index=True)
        display(df)

    @staticmethod
    def decorate_all_standard_methods(
            active: bool = True, log_sql: bool = False):
        methods = ModelStatsSetsManager.get_docfieldrepo_methods() + \
                  ModelStatsSetsManager.get_field_locators() + \
                  ModelStatsSetsManager.get_fields_detecting_methods() + \
                  ModelStatsSetsManager.get_common_locators()
        ModelStatsSetsManager.decorate_methods(methods, active=active, log_sql=log_sql)
        print(f'decorate_all_standard_methods - {len(methods)} methods are decorated')

    @staticmethod
    def purge_stored_statistics():
        count = MethodStats.objects.all().count()
        MethodStats.objects.all().delete()
        print(f'Deleted {count} MethodStats records')
