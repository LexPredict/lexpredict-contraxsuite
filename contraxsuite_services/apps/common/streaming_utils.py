import csv
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
