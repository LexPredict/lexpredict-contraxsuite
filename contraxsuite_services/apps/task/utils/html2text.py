# -*- coding: utf-8 -*-
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"

# Standard imports
import html
import json
import os

# HTML/requests imports
import html2text
import requests


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
