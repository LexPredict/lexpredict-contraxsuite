import sys
from datetime import datetime, date
from typing import List, Union, Callable, Dict


class VectorizerStep:
    def fit(self, field_values_or_anything: List, *args, **kwargs):
        return self

    def fit_transform(self, field_values_or_anything: List, *args, **kwargs):
        self.fit(field_values_or_anything)
        return self.transform(field_values_or_anything)

    def transform(self, field_values_or_anything: List, *args, **kwargs):
        pass


def whole_value_as_token(value: str) -> List[str]:
    return [str(value)]


def list_items_as_tokens(value: List) -> List[str]:
    return [str(i) for i in value]


class ReplaceNoneTransformer(VectorizerStep):
    def __init__(self, default_value) -> None:
        super().__init__()
        self.default_value = default_value

    def transform(self, field_values_or_anything: List, *args, **kwargs):
        return [v or self.default_value for v in field_values_or_anything]


class DictItemSelector(VectorizerStep):
    def __init__(self, item: str, processor: Callable = None) -> None:
        super().__init__()
        self.item = item
        self.processor = processor if processor else lambda x: x

    def transform(self, field_values_or_anything: List[Dict], *args, **kwargs):
        return [self.processor(d.get(self.item) if d else None) for d in field_values_or_anything]


class RecurringDateVectorizer(VectorizerStep):
    MAX_YEAR = 2050
    MIN_YEAR = 1970

    def transform(self, field_values: List[Union[datetime, date]], *args, **kwargs):
        # TODO Optimize list manipulations

        res = list()
        for d in field_values:
            vect = list()

            year = d.year if d else 1  # 1 - 9999
            year = 0 if year < self.MIN_YEAR else self.MAX_YEAR if year > self.MAX_YEAR else year
            year = year - self.MIN_YEAR
            year_vect = [1 if i == year else 0 for i in range(self.MAX_YEAR - self.MIN_YEAR)]
            vect.extend(year_vect)

            month = d.month - 1 if d else 0  # 0 - 11
            month_vect = [1 if month == i else 0 for i in range(11)]
            vect.extend(month_vect)

            day = d.day - 1 if d else 0  # 0 - 30
            day_vect = [1 if day == i else 0 for i in range(30)]
            vect.extend(day_vect)

            day_of_week = d.weekday() if d else 0  # M0 - S6
            dow_vect = [1 if day_of_week == i else 0 for i in range(6)]
            vect.extend(dow_vect)

            res.append(vect)
        return res


class SerialDateVectorizer(VectorizerStep):
    MAX_YEAR = 2050
    MIN_YEAR = 1970

    def transform(self, field_values: List[Union[datetime, date]], *args, **kwargs):
        # TODO Optimize list manipulations

        res = list()
        for d in field_values:
            vect = list()

            year = d.year if d else 1  # 1 - 9999
            year = 0 if year < self.MIN_YEAR else self.MAX_YEAR if year > self.MAX_YEAR else year
            year = year - self.MIN_YEAR
            vect.append(year / (self.MAX_YEAR - self.MIN_YEAR))

            month = d.month - 1 if d else 0  # 0 - 11
            vect.append(month / 11)

            day = d.day - 1 if d else 0  # 0 - 30
            vect.append(day / 30)

            day_of_week = d.weekday() if d else 0  # M0 - S6
            vect.append(day_of_week / 6)

            res.append(vect)
        return res


class NumberVectorizer(VectorizerStep):
    def __init__(self, to_float_converter: Callable = None) -> None:
        super().__init__()
        self.to_float_converter = to_float_converter if to_float_converter else \
            lambda n: float(n) if n is not None else 0
        self.min_value = sys.float_info.min
        self.max_value = sys.float_info.max

    def fit(self, field_values_or_anything: List, *args, **kwargs):
        min_value = sys.float_info.min
        max_value = sys.float_info.max

        for n in field_values_or_anything:
            n = self.to_float_converter(n)
            if n < min_value:
                min_value = n
            if n > max_value:
                max_value = n

        self.min_value = min_value
        self.max_value = max_value
        return self

    def fit_transform(self, field_values_or_anything: List, *args, **kwargs):
        self.fit(field_values_or_anything)
        return self.transform(field_values_or_anything)

    def transform(self, field_values_or_anything: List, *args, **kwargs):
        res = list()
        for n in field_values_or_anything:
            n = self.to_float_converter(n) if self.to_float_converter else float(n)
            n = (n - self.min_value) / (self.max_value - self.min_value)
            res.append([n])
        return res
