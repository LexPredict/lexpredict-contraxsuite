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
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import regex as re
from typing import Set, Optional, Callable


class UniqueNameBuilder:
    reg_name_copy_part = re.compile(r'\scopy\s\d{2,2}$')

    @classmethod
    def make_doc_unique_name(cls,
                             doc_name: str,
                             project_doc_names: Set[str],
                             unique_strict_check: Optional[Callable[[str], bool]] = None):

        def new_name_is_unique(new_name: str) -> bool:
            if new_name in project_doc_names:
                return False
            if unique_strict_check and not unique_strict_check(new_name):
                return False
            return True

        if new_name_is_unique(doc_name):
            return doc_name

        # make document a unique name
        name, ext = os.path.splitext(doc_name)
        # ... try filename w/o " copy 01"
        name = cls.reg_name_copy_part.sub('', name)
        new_name = name + ext
        counter = 1
        while not new_name_is_unique(new_name):
            new_name = f'{name} copy {counter:02d}{ext}'
            counter += 1
        return new_name
