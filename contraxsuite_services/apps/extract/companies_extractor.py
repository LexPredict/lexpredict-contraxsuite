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

from typing import Optional, List

from lexnlp.extract.common.entities.entity_banlist import BanListUsage

from apps.extract.company_types import CompanyTypeCache
from apps.extract.models import BanListRecord

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CompaniesExtractor:
    @classmethod
    def get_companies(cls,
                      project_id: Optional[int],
                      text: str,
                      strict: bool = False,
                      use_gnp: bool = False,
                      detail_type: bool = False,
                      count_unique: bool = False,
                      name_upper: bool = False,
                      parse_name_abbr: bool = False,
                      return_source: bool = False,
                      selected_tags: Optional[List[str]] = None):
        _filter = cls.get_banlist_filter()
        detector = CompanyTypeCache.get_company_detector(project_id, selected_tags)

        return detector.get_companies(
            text,
            strict=strict,
            use_gnp=use_gnp,
            detail_type=detail_type,
            count_unique=count_unique,
            name_upper=name_upper,
            parse_name_abbr=parse_name_abbr,
            return_source=return_source,
            banlist_usage=_filter)

    @classmethod
    def get_banlist_filter(cls) -> BanListUsage:
        filter_settings = BanListUsage()
        filter_records = [r for r in BanListRecord.get_cached()
                          if r.entity_type == BanListRecord.TYPE_PARTY]
        if filter_records:
            filter_settings.banlist = [r.to_banlist_item() for r in filter_records]
            filter_settings.append_to_default = True
        return filter_settings
