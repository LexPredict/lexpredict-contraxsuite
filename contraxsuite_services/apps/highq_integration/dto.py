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

import datetime
from typing import Dict, List, Union

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class HighQDTO:
    def to_dict(self):
        """
        BASED ON OPENAPI
        """
        d: Dict = {}
        for attribute, value in self.__dict__.items():
            if value is None:
                continue
            if isinstance(value, list):
                d[attribute] = list(
                    map(
                        lambda x:
                            x.to_dict()
                            if hasattr(x, 'to_dict')
                            else x,
                        value
                    )
                )
            elif hasattr(value, 'to_dict'):
                d[attribute] = value.to_dict()
            elif isinstance(value, dict):
                d[attribute] = dict(
                    map(
                        lambda item:
                            (item[0], item[1].to_dict())
                            if hasattr(item[1], 'to_dict')
                            else item,
                        value.items()
                    )
                )
            else:
                d[attribute] = value
        return d

    def sanitize_for_serialization(self, obj):
        """
        BASED ON OPENAPI
        Builds a Dict for a JSON POST object.
        """
        if obj is None:
            return None
        if isinstance(obj, (bool, bytes, str, int, float,)):
            return obj
        if isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj) for sub_obj in obj]
        if isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj) for sub_obj in obj)
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            obj_dict = {
                attribute: getattr(obj, attribute)
                for attribute in obj.__dict__.keys()
                if getattr(obj, attribute) is not None
            }
        return {
            key: self.sanitize_for_serialization(value)
            for key, value in obj_dict.items()
        }

    def __eq__(self, other) -> bool:
        """Returns true if both objects are equal"""
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()

    def __ne__(self, other) -> bool:
        """Returns true if both objects are not equal"""
        if not isinstance(other, self.__class__):
            return True
        return self.to_dict() != other.to_dict()


class ChoiceDTO(HighQDTO):
    def __init__(
        self,
        id: int = None,
        label: str = None,
        score: str = None,
        color: str = None,
        imageid: int = None,
    ) -> None:
        self.id: str = str(id)
        self.label: str = label
        self.score: str = score
        self.color: str = color
        self.imageid: str = str(imageid) if imageid is not None else ''


class ChoicesDTO(HighQDTO):
    def __init__(
        self,
        choice: List[ChoiceDTO] = None,
    ) -> None:
        self.choice: List[ChoiceDTO] = choice


# noinspection SpellCheckingInspection
class DocumentDTO(HighQDTO):
    def __init__(
        self,
        docid: int = None,
    ) -> None:
        """
        TODO: there are many other parameters defined in Swagger
        """
        self.docid: int = docid


class DocumentsDTO(HighQDTO):
    def __init__(
        self,
        document: List[DocumentDTO] = None,
    ) -> None:
        self.document: List[DocumentDTO] = document


class RawDataDTO(HighQDTO):
    def __init__(
        self,
        value: str = None,
        date: str = None,
        time: str = None,
        choices: ChoicesDTO = None,
        documents: DocumentsDTO = None,
    ) -> None:
        """
        TODO: there are many other parameters defined in Swagger
        """
        self.value: str = value
        self.date: str = date
        self.time: str = time
        self.choices: ChoicesDTO = choices
        self.documents: DocumentsDTO = documents


# noinspection SpellCheckingInspection
class ColumnDTO(HighQDTO):
    def __init__(
        self,
        attributecolumnid: int = None,
        rawdata: RawDataDTO = None,
    ) -> None:
        """
        TODO: there are many other parameters defined in Swagger
        """
        self.attributecolumnid: str = str(attributecolumnid)
        self.rawdata: RawDataDTO = rawdata


# noinspection SpellCheckingInspection
class ItemDTO(HighQDTO):
    def __init__(
        self,
        itemid: int = None,
        externalid: Union[int, str] = None,
        column: List[ColumnDTO] = None,
    ) -> None:
        self.itemid: str = str(itemid)
        self.externalid: str = \
            str(externalid) if externalid is not None else ''
        self.column: List[ColumnDTO] = column


class DataDTO(HighQDTO):
    def __init__(
        self,
        item: List[ItemDTO] = None,
    ) -> None:
        self.item: List[ItemDTO] = item


class ISheetDTO(HighQDTO):
    def __init__(
        self,
        data: DataDTO = None,
    ) -> None:
        self.data: DataDTO = data
