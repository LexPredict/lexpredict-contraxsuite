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

import codecs
import json
import os
from typing import Tuple, List, Dict, Optional

import msgpack
from PIL import Image, ImageDraw

from apps.document.models import DocumentPDFRepresentation
from tests.testutils import TEST_RESOURCE_DIRECTORY

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def load_sample_pdf_data() -> Tuple[DocumentPDFRepresentation, str]:
    file_path = os.path.join(TEST_RESOURCE_DIRECTORY, 'documents/pdf_coordinates/three_pages_pages.json')
    with open(file_path, 'r') as f:
        pages = json.load(f)

    file_path = os.path.join(TEST_RESOURCE_DIRECTORY, 'documents/pdf_coordinates/three_pages_boxes.json')
    with open(file_path, 'r') as f:
        boxes = json.load(f)

    pdf_data = DocumentPDFRepresentation()
    pdf_data.set_pages(pages)
    pdf_data.char_bboxes = msgpack.packb({'char_bboxes': boxes},
                                         use_bin_type=True, use_single_float=True)

    file_path = os.path.join(TEST_RESOURCE_DIRECTORY, 'documents/pdf_coordinates/three_pages_text.txt')
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        file_text = f.read()

    return pdf_data, file_text


def render_boxes(boxes: List[List[float]],
                 image_file_name: str,
                 default_color: str = 'black',
                 color_by_index: Dict[int, str] = None,
                 selected_point: Optional[Tuple[float, float]] = None,
                 selected_point_color: str = 'red',
                 text: Optional[str] = None,
                 scale: float = 1.0):
    file_path = os.path.join(TEST_RESOURCE_DIRECTORY,
                             'documents/pdf_coordinates/rendered/',
                             image_file_name)

    color_by_index = color_by_index or {}
    width = max([b[0] + b[2] for b in boxes if b])
    height = max([b[1] + b[3] for b in boxes if b])

    img = Image.new('RGB',
                    (int(round(width * scale)) + 2,
                     int(round(height * scale)) + 2),
                    color='white')
    d = ImageDraw.Draw(img)

    for n, item in enumerate(boxes):
        if not item:
            continue
        x, y, w, h = item[0] * scale, item[1] * scale, \
            item[2] * scale, item[3] * scale
        color = color_by_index.get(n, default_color)
        d.rectangle([(x, y), (x + w, y + h)], outline=color)
        txt = text[n] if text and n < len(text) else str(n)
        d.text((x + 2, y + 2), txt, fill=color)

    if selected_point:
        x, y = selected_point[0] * scale, selected_point[1] * scale
        d.line((x - 1, y) + (x - 3, y), fill=selected_point_color)
        d.line((x + 1, y) + (x + 3, y), fill=selected_point_color)
        d.line((x, y + 1) + (x, y + 3), fill=selected_point_color)
        d.line((x, y - 1) + (x, y - 3), fill=selected_point_color)

    img.save(file_path)
