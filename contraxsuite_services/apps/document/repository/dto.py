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

from typing import Any, Optional, List

from dataclasses import dataclass
from dataclasses_json import dataclass_json

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@dataclass_json
@dataclass
class AnnotationDTO:
    """
    Representes FieldAnnotation object as it is transferred between frontend, backend and database.
    Substantiates the corresponding field value. Main content of the annotation is the location of the
    text block.
    Additionally it contains some more hints substantiating the field value:
        annotation_value - part of the whole field value to which this annotation is bound (works for multi-choices);
        extraction_hint_name - name of the extraction hint used to detect this annotation by auto field detection.

    Annotation value is in JSON format, not in Python. See field_types.py/RawdbFieldHandler.annotation_value_python_to_json().
    """
    annotation_value: Any
    location_in_doc_start: int
    location_in_doc_end: int
    extraction_hint_name: Optional[str] = None


@dataclass_json
@dataclass
class FieldValueDTO:
    """
    Represents FieldValue object as it is transferred between frontend, backend and database.
    FieldValueDTO may contain zero or more text annotations representing blocks of text containing
    information substantiating the field value.
    Values are in JSON format, not in python. See field_types.py/RawdbFieldHandler.annotation_value_python_to_json().
    """
    field_value: Any
    annotations: Optional[List[AnnotationDTO]] = None
