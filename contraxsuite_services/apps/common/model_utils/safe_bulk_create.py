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


from typing import List, Any, Callable, Optional
import regex as re
from django.db import models
from django.db.utils import IntegrityError as UtilIntegrityError
from django.db import IntegrityError


class SafeBulkCreate:
    """
    Similar to Manager.bulk_create with ignore_conflicts = True,
    but also ignores FK errors
    """
    @classmethod
    def bulk_create(cls, object_manager: models.Manager, objects: List[Any]) -> int:
        if not objects:
            return 0
        try:
            object_manager.bulk_create(objects, ignore_conflicts=True)
            return len(objects)
        except (IntegrityError, UtilIntegrityError) as e:
            if len(objects) < 2:
                return 0
            # remove failing entities
            ent_filter = cls.build_entity_filter(str(e))
            if ent_filter:
                objects = [o for o in objects if not ent_filter(o)]

            if len(objects) == 1:
                return cls.bulk_create(object_manager, objects)

            # split whole sequence in two and try
            half = int(len(objects) / 2)
            left_count = cls.bulk_create(object_manager, objects[:half])
            right_count = cls.bulk_create(object_manager, objects[half:])
            return left_count + right_count

    @classmethod
    def build_entity_filter(cls, integrity_error: str) -> Optional[Callable[[Any], bool]]:
        """
        insert or update on table "extract_partyusage" violates foreign key constraint
        "extract_partyusage_text_unit_id_2b4758b0_fk_document_"
        DETAIL:  Key (text_unit_id)=(2614539) is not present in table "document_textunit".
        """
        match = re.search(r'Key \([^\)]+\)=\([^\)]+\) is not present', integrity_error)
        if not match:
            return None
        match_str = match.group(0)[len('Key '):]
        match_str = match_str[:-len(' is not present')]
        match_parts = [g for g in re.findall(r'\([^\)]+\)', match_str)]
        if len(match_parts) != 2:
            return None

        key_value = []  # [['text_unit_id'], ['2614539']]
        for part in match_parts:
            items_str = part.strip('() ')
            items_parts = items_str.split(',')
            key_value.append([p.strip() for p in items_parts])

        # build filter expression
        def filter_expr(item: Any) -> bool:
            try:
                keys = key_value[0]
                values = key_value[1]
                for i in range(len(keys)):
                    # casting PK value to string is OK because our key is supposed to be
                    # either int or str
                    obj_val = str(getattr(item, keys[i]))
                    if obj_val != values[i]:
                        return False
                return True
            except:
                return False

        return filter_expr
