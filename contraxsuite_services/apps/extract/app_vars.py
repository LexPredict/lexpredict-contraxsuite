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

# Project imports
from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


STANDARD_LOCATORS = AppVar.set(
    'Extract', 'standard_locators',
    ['citation',
     'currency',
     'date',
     'definition',
     'duration',
     'geoentity',
     'party',
     'term'],
    'List of standard (required) locators for use in "Load Documents" task.',
    system_only=False)

OPTIONAL_LOCATORS = AppVar.set(
    'Extract', 'optional_locators',
    ['amount',
     'copyright',
     'court',
     'distance',
     'percent',
     'ratio',
     'regulation',
     'trademark',
     'url'],
    'List of optional locators for use additionally '
    'in "Locate" task if they have been chosen in "Locate" form.',
    system_only=False)

SIMPLE_LOCATOR_TOKENIZATION = AppVar.set(
    'Extract', 'simple_locator_tokenization', True,
    """<ul>
          <li><code>true</code>: use regex tokenization when locating Courts and GeoEntities,</li>
          <li><code>false</code>: use tokenization.</li>
       </ul>""",
    system_only=False)

STRICT_PARSE_DATES = AppVar.set(
    'Extract', 'strict_parse_dates', True,
    """
    <ul>
       <li><code>true</code>: skip values like "C-4-30"</li>          
    </ul>
    """, system_only=False)
