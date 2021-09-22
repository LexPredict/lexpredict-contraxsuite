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

from typing import Tuple, List, Optional, Any, Dict

from apps.document.pdf_coordinates.pdf_coords_commons import XYWH, Dir, SelectionArea

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextCoordMap:
    @classmethod
    def get_line_areas(
            cls,
            doc_char_boxes: List[XYWH],
            doc_pages: List[Dict[str, Any]],
            location_start: int,
            location_end: int) -> List[SelectionArea]:
        # find pages for the selected fragment
        pages: List[Tuple[int, int, int]] = []  # [(page, start, end), ...]
        for i in range(len(doc_pages)):
            p_start, p_end = doc_pages[i]['start'], doc_pages[i]['end']

            # ...<....>..s...e.
            if location_start >= p_end:
                continue

            # ...s..<....>....e...
            if location_start <= p_start and location_end >= p_end:
                pages.append((i, p_start, p_end))
                continue

            # ....<.s.....e....>..
            if p_start <= location_start and p_end >= location_end:
                pages.append((i, location_start, location_end))
                continue

            # ...s..e...<......>....
            if location_end < p_start:
                break

            # .....<...s...e..>.. OR ....<..s....>..e...
            if location_end >= p_start:
                pages.append((i, max(p_start, location_start), min(location_end, p_end)))
                continue
            # ....<..s...e..>.. OR ..<..s....>...e
            # if location_start < p_end:
            #    pages.append((i, min(p_start, location_start), p_end))
            #    continue

        page_areas = []
        for page_num, start, end in pages:
            page_areas += cls.get_page_line_areas(page_num, doc_char_boxes, start, end)

        return page_areas

    @classmethod
    def extend_rect(cls,
                    text_dir: Optional[Dir],
                    rect: XYWH,
                    next_possible_rect: XYWH) -> Tuple[Optional[Dir], Optional[XYWH]]:
        ox, oy, ow, oh = rect
        nx, ny, nw, nh = next_possible_rect

        # test extending to left or right
        # it can work only if the original rectangle was horizontal or a square
        # and they should be very close by vertical axis
        if (text_dir is None or text_dir == Dir.horizontal) \
                and abs(oy - ny) <= 0.2 * oh and abs((oy + oh) - (ny + nh)) <= 0.2 * oh:
            rx = min(ox, nx)
            ry = min(oy, ny)
            rx2 = max(ox + ow, nx + nw)
            rw = rx2 - rx
            rh = max(oh, nh)
            return Dir.horizontal, (rx, ry, rw, rh)

        # testing for vertical extension - up and down
        if (text_dir is None or text_dir == Dir.vertical) \
                and abs(ox - nx) <= 0.2 * ow and abs((ox + ow) - (nx + nw)) <= 0.2 * ow:
            rx = min(ox, nx)
            ry = min(oy, ny)
            ry2 = max(oy + oh, ny + nh)
            rh = ry2 - ry
            rw = max(ow, nw)
            return Dir.vertical, (rx, ry, rw, rh)

        # otherwise the rectangles are not close enough in any direction (TODO: deskew angles?)
        return None, None

    @classmethod
    def get_page_line_areas(
            cls,
            page_num: int,
            doc_char_boxes: List[XYWH],
            location_start: int,
            location_end: int) -> List[SelectionArea]:
        if location_start == location_end:
            return []
        if location_start > location_end:
            location_start, location_end = location_end, location_start

        areas = []
        cur_rect: Optional[XYWH] = doc_char_boxes[location_start]
        text_direction: Optional[Dir] = None
        for i in range(location_start + 1, location_end):
            char_box = doc_char_boxes[i]
            if not char_box or not char_box[2] or not char_box[3]:
                continue

            extended_text_direction, extended_rect = cls.extend_rect(text_direction, cur_rect, char_box)
            if not extended_text_direction:
                if cur_rect[2] and cur_rect[3]:
                    areas.append(SelectionArea(page=page_num, area=cur_rect))
                cur_rect = char_box
                text_direction = None
            else:
                cur_rect = extended_rect
                text_direction = extended_text_direction
        if cur_rect and cur_rect[2] and cur_rect[3]:
            areas.append(SelectionArea(page=page_num, area=cur_rect))
        return areas
