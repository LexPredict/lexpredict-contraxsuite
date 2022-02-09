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

import os
import re
import random
from io import BytesIO

from cairosvg import svg2png
from xml.sax.saxutils import escape as xml_escape
from django.core.files import File
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_main_admin_user() -> User:
    return User.objects.get_by_natural_key('Administrator')


COLORS = [
    ['#DF7FD7', '#DF7FD7', '#591854'],
    ['#E3CAC8', '#DF8A82', '#5E3A37'],
    ['#E6845E', '#E05118', '#61230B'],
    ['#E0B050', '#E6CB97', '#614C23'],
    ['#9878AD', '#492661', '#C59BE0'],
    ['#787BAD', '#141961', '#9B9FE0'],
    ['#78A2AD', '#104F61', '#9BD1E0'],
    ['#78AD8A', '#0A6129', '#9BE0B3'],
]

INITIALS_SVG_TEMPLATE = """
<svg version="1.1" baseProfile="full"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0, 0, 100, 100">
  <circle cx="50" cy="50" r="49" fill="{color}" stroke="#ffffff" stroke-width="1" class="la2-circle" />
  <text x="50" y="71.5" font-family="Arial" font-size="60"
    font-weight="700" text-anchor="middle" fill="#ffffff" class="la2-text">{initials}</text>
</svg>""".strip()

INITIALS_SVG_TEMPLATE = re.sub(r'(\s+|\n)', ' ', INITIALS_SVG_TEMPLATE)


def save_default_avatar(user, save=False):
    random_color = random.choice(COLORS)
    svg_avatar = INITIALS_SVG_TEMPLATE.format(**{
        'color': random_color[0],
        'initials': xml_escape(user.initials.upper()),
        'username': user.username
    }).replace('\n', '')
    output_file = BytesIO()
    svg2png(svg_avatar, write_to=output_file)
    user.photo.save(os.path.basename(f'{user.username}.png'), File(output_file))
    if save:
        user.save()
