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

from collections import defaultdict
from math import isclose
from typing import Optional, List, Dict, Any, Set, Tuple

from apps.document.models import DocumentPDFRepresentation
from apps.document.pdf_coordinates.pdf_coords_commons import XYWH

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CoordTextMap:

    @classmethod
    def area(cls, a: XYWH) -> float:
        return a[2] * a[3]

    @classmethod
    def overlap_area(cls, a: XYWH, b: XYWH) -> float:
        dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
        dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
        if (dx >= 0) and (dy >= 0):
            return dx * dy
        return 0

    @classmethod
    def xywh_overlap(cls, r1: XYWH, r2: XYWH) -> bool:
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    @classmethod
    def overlaps_any_sel_area_on_page(cls, char_area: float, char_bbox: XYWH, page_test_areas: Set[XYWH]) -> bool:
        for sel_area in page_test_areas:
            if cls.overlap_area(sel_area, char_bbox) > 0.2 * char_area:
                return True
        return False

    @classmethod
    def find_longest_continuous_location(cls,
                                         doc_char_bboxes: List[XYWH],
                                         sel_area: XYWH,
                                         page_loc_start: int,
                                         page_loc_end: int,
                                         debug_full_text: str = None) -> Tuple[int, int]:
        longest_location: Optional[Tuple[int, int]] = None
        location_start: Optional[int] = None
        location_end: Optional[int] = None
        for location in range(page_loc_start, page_loc_end):
            char_bbox = doc_char_bboxes[location]
            # ignore non-printable characters
            if char_bbox[2] < 0.00001 or char_bbox[3] < 0.00001:
                continue
            if cls.overlap_area(sel_area, char_bbox) > 0.2 * cls.area(char_bbox):
                if location_start is None:
                    location_start = location
                    location_end = location
                else:
                    location_end = location
            elif location_start is not None:
                if longest_location is None \
                        or location_end - location_start > longest_location[1] - longest_location[0]:
                    longest_location = location_start, location_end
                location_start = None
                location_end = None

        # if selection continues til the end of the page
        if longest_location is None and location_start is not None:
            longest_location = location_start, location_end

        return longest_location

    @classmethod
    def get_text_location_by_coords(
            cls,
            document_id: int,
            selections: List[Dict[str, Any]]):
        pdf_data = list(DocumentPDFRepresentation.objects.filter(document_id=document_id))
        if not pdf_data:
            raise Exception(f'The document #{document_id} doesn\'t have a PDF binding')

        # debug
        # from apps.document.models import DocumentText
        # doc_text = DocumentText.objects.get(document_id=document_id).full_text

        # number, start, end, bbox
        pages: List[Dict[str, Any]] = pdf_data[0].pages_list
        doc_char_bboxes: List[XYWH] = pdf_data[0].char_bboxes_list

        location_start: Optional[int] = None
        location_end: Optional[int] = None
        for selection in selections:
            page: int = selection['page']
            sel_areas: List[XYWH] = selection['areas']  # areas should be replaced with first_bbox/last_bbox
            page_loc_start: int = pages[page]['start']
            page_loc_end: int = pages[page]['end']

            for sel_area in sel_areas:
                sel_area_location: Tuple[int, int] = \
                    cls.find_longest_continuous_location(doc_char_bboxes=doc_char_bboxes,
                                                         sel_area=sel_area,
                                                         page_loc_start=page_loc_start,
                                                         page_loc_end=page_loc_end)  # , debug_full_text=doc_text)
                if sel_area_location:
                    location_start = min(location_start, sel_area_location[0]) \
                        if location_start is not None \
                        else sel_area_location[0]
                    location_end = max(location_end, sel_area_location[1]) \
                        if location_end is not None \
                        else sel_area_location[1]

        if location_start is None:
            raise Exception(f'No text found for the specified selection PDF coordinates')

        return location_start, (location_end or location_start) + 1

    @classmethod
    def get_text_location_by_coords_needs_all_sel_areas(
            cls,
            document_id: int,
            selections: List[Dict[str, Any]]):
        pdf_data = list(DocumentPDFRepresentation.objects.filter(document_id=document_id))
        if not pdf_data:
            raise Exception(f'The document #{document_id} doesn\'t have a PDF binding')

        # debug
        # from apps.document.models import DocumentText
        # pdf_text = DocumentText.objects.get(document_id=document_id).full_text

        # number, start, end, bbox
        pages: List[Dict[str, Any]] = pdf_data[0].pages_list
        doc_char_bboxes: List[XYWH] = pdf_data[0].char_bboxes_list

        test_page_num_first: Optional[int] = None
        test_page_num_last: Optional[int] = None
        test_areas_by_page: Dict[int, Set[XYWH]] = defaultdict(set)
        for selection in selections:
            page_num: int = selection['page']
            sel_areas: List[XYWH] = selection['areas']  # areas should be replaced with first_bbox/last_bbox
            test_page_num_first = max(test_page_num_first, page_num)
            test_page_num_last = min(test_page_num_last, page_num)
            test_areas_by_page[page_num].update(sel_areas)

        location_first: Optional[int] = None
        location_last: Optional[int] = None
        for test_page_num in range(test_page_num_first, test_page_num_last + 1):
            test_char_location_start: int = pages[test_page_num]['start']
            test_char_location_end: int = pages[test_page_num]['end']
            page_test_areas = test_areas_by_page[test_page_num]
            for test_char_location in range(test_char_location_start, test_char_location_end):
                test_char_bbox = doc_char_bboxes[test_char_location]
                test_char_area = cls.area(test_char_bbox)
                if isclose(test_char_area, 0, abs_tol=1e-10):
                    continue
                if cls.overlaps_any_sel_area_on_page(test_char_area, test_char_bbox, page_test_areas):
                    if location_first is None:
                        location_first = test_char_location
                    location_last = test_char_location
                else:
                    if location_first is not None:
                        break

        if location_first is None:
            raise Exception(f'No text found for the specified selection PDF coordinates')

        return location_first, location_last + 1
