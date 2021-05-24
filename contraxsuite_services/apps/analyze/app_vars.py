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


NOTIFY_TOO_MANY_DOCUMENTS = AppVar.set(
    'Analyze', 'cluster_documents_limit', 1000,
    'Notify if there are too many documents for clustering'
)

NOTIFY_TOO_MANY_UNITS = AppVar.set(
    'Analyze', 'cluster_text_units_limit', 500000,
    'Notify if there are too many text units for clustering'
)

DOCUMENT_SIMILARITY_OBJECTS_EXPIRE_IN = AppVar.set(
    'Analyze', 'document_similarity_objects_expire_in', 30 * 24 * 60 * 60,
    'Delete DocumentSimilarity objects in N sec after they were created'
)

TEXT_UNIT_SIMILARITY_OBJECTS_EXPIRE_IN = AppVar.set(
    'Analyze', 'text_unit_similarity_objects_expire_in', 2 * 24 * 60 * 60,
    'Delete TextUnitSimilarity objects in N sec after they were created'
)

SIMILARITY_MAX_BASE = AppVar.set(
    'Analyze', 'similarity_max_base', 50000,
    'Maximum allowed number of items to start similarity process'
)
