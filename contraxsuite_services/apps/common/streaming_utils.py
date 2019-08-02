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

import csv
import os
import tempfile
from contextlib import contextmanager
from types import GeneratorType
from typing import BinaryIO
from typing import Generator, Any, List

from django.core.serializers.json import DjangoJSONEncoder
from requests.models import Response

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Echo:
    def write(self, value):
        return value


class GeneratorList(list):
    def __init__(self, generator: Generator) -> None:
        super().__init__()
        self.generator = generator

    def __iter__(self):
        return self.generator

    def __len__(self):
        return 1


def csv_gen(column_names: List[str], rows: Generator[List, None, None], column_titles: List[str] = None) \
        -> Generator[str, None, None]:
    writer = csv.writer(Echo())
    yield writer.writerow(column_titles if column_titles else column_names)
    for row in rows:
        yield writer.writerow(row)


def csv_gen_from_dicts(rows: GeneratorType, fieldnames=None) -> Generator[str, None, None]:
    first_row = None
    if fieldnames is None:
        first_row = next(rows)
        fieldnames = first_row.keys()
    writer = csv.DictWriter(Echo(), fieldnames=fieldnames)
    yield writer.writerow(dict(zip(fieldnames, fieldnames)))
    if first_row is not None:
        yield writer.writerow(first_row)
    for row in rows:
        yield writer.writerow(row)


def json_gen(v: Any, encoder=None) -> Generator[str, None, None]:
    if not encoder:
        encoder = DjangoJSONEncoder()

    yield from encoder.iterencode(v)


BUFFER_SIZE = 4096


@contextmanager
def buffer_contents_into_temp_file(http_response, file_suffix: str) -> Generator[str, None, None]:
    _fd, fn = tempfile.mkstemp(suffix=file_suffix)
    try:
        with open(fn, 'bw') as f:
            for chunk in http_response.iter_content(chunk_size=BUFFER_SIZE):
                if chunk:
                    f.write(chunk)
        http_response.close()
        yield fn
    finally:
        http_response.close()
        os.remove(fn)


def copy_data(src_file_like_object: BinaryIO, dst_file_like_object: BinaryIO):
    chunk = src_file_like_object.read(BUFFER_SIZE)
    while chunk:
        dst_file_like_object.write(chunk)
        chunk = src_file_like_object.read(BUFFER_SIZE)


def download_file(http_response: Response, fn: str):
    with open(fn, 'bw') as f:
        for chunk in http_response.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    http_response.close()
