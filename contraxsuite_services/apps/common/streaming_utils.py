import csv
import os
import tempfile
from contextlib import contextmanager
from typing import Generator, Any, List

from django.core.serializers.json import DjangoJSONEncoder


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


def json_gen(v: Any, encoder=None) -> Generator[str, None, None]:
    if not encoder:
        encoder = DjangoJSONEncoder()

    yield from encoder.iterencode(v)


@contextmanager
def buffer_contents_into_file(filename, http_response) -> Generator[str, None, None]:
    _, ext = os.path.splitext(filename) if filename else None
    _fd, fn = tempfile.mkstemp(suffix=ext)
    try:
        with open(fn, 'bw') as f:
            for chunk in http_response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        http_response.close()
        yield fn
    finally:
        http_response.close()
        os.remove(fn)
