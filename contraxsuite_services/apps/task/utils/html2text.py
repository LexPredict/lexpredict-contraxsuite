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
# Standard imports
import html
import json
import os

# HTML/requests imports
import html2text
import requests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.1c/LICENSE"
__version__ = "1.1.1c"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def is_html_doc(input_buffer, encoding="utf-8", bracket_threshold=0.005):
    """
    Check if the given input buffer is an HTML/XML/XHTML document.
    :param input_buffer: input buffer
    :param encoding: default encoding
    :param bracket_threshold: angle bracket (<>) threshold
    :return:
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding).lower()

    # Check for tag
    if "<html" in input_buffer or "<xml" in input_buffer:
        return True

    # Check threshold
    bracket_count = float(input_buffer.count("<")) + float(input_buffer.count(">"))
    if bracket_count / len(input_buffer) > bracket_threshold:
        return True

    # Otherwise, return false.
    return False


def export_html_to_text_html2text(input_buffer, encoding="utf-8"):
    """
    Export HTML to text via html2text.
    :param input_buffer: input HTML buffer
    :param encoding: default encoding
    :return:
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding)

    # Process and return
    parser = html2text.HTML2Text()
    parser.ignore_emphasis = True
    parser.ignore_links = True
    parser.ignore_images = True
    html_buffer = html.unescape(parser.handle(input_buffer))
    return html_buffer


def export_html_to_text_tika(input_buffer, encoding="utf-8", tika_endpoint=None):
    """
    Export HTML to text via tika.
    :param input_buffer: input HTML buffer
    :param encoding: default encoding
    :param tika_endpoint:
    :return:
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        try:
            input_buffer = input_buffer.decode(encoding)
        except:
            pass

    # Check for endpoint
    if not tika_endpoint:
        tika_endpoint = os.environ["TIKA_SERVER_ENDPOINT"]

    # Setup request
    response = requests.put(
        "{0}/rmeta/text".format(tika_endpoint.strip("/")),
        data=input_buffer,
        headers={})
    json_data = json.loads(response.content.decode("utf-8")).pop()
    json_data["content"] = json_data["X-TIKA:content"]
    del json_data["X-TIKA:content"]

    return json_data
