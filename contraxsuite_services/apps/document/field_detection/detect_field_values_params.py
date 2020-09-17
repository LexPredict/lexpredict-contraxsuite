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

from typing import List

from apps.common.log_utils import auto_str
from apps.common.utils import Serializable
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@auto_str
class DocDetectFieldValuesParams(Serializable):
    def __init__(self,
                 document_id: int,
                 do_not_write: bool = False,
                 clear_old_values: bool = True,
                 updated_field_codes: List[str] = None,
                 user: User = None,
                 skip_modified_values: bool = True,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.document_id = document_id
        self.do_not_write = do_not_write
        self.clear_old_values = clear_old_values
        self.updated_field_codes = updated_field_codes
        self.user = user
        self.skip_modified_values = skip_modified_values
