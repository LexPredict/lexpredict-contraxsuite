from enum import Enum, unique
from typing import Optional, List

EH_TAKE_MIN = 'TAKE_MIN'
EH_TAKE_MAX = 'TAKE_MAX'

ORDINAL_EXTRACTION_HINTS = [EH_TAKE_MIN, EH_TAKE_MAX]


@unique
class ValueExtractionHint(Enum):
    TAKE_FIRST = 'TAKE_FIRST'
    TAKE_SECOND = 'TAKE_SECOND'
    TAKE_LAST = 'TAKE_LAST'
    TAKE_MIN = EH_TAKE_MIN
    TAKE_MAX = EH_TAKE_MAX

    @staticmethod
    def _is_money(v) -> bool:
        return type(v) is dict and 'amount' in v and 'currency' in v

    @staticmethod
    def get_value(l: Optional[List], hint: str):
        if not l:
            return None

        if str(hint) == ValueExtractionHint.TAKE_LAST.name:
            return l[-1]
        elif str(hint) == ValueExtractionHint.TAKE_SECOND.name and len(l) > 1:
            return l[1]
        elif str(hint) == ValueExtractionHint.TAKE_FIRST.name and len(l) > 0:
            return l[0]
        elif str(hint) == ValueExtractionHint.TAKE_MIN.name:
            return min(l, key=lambda dd: dd['amount']) if ValueExtractionHint._is_money(l[0]) else min(l)
        elif str(hint) == ValueExtractionHint.TAKE_MAX.name:
            return max(l, key=lambda dd: dd['amount']) if ValueExtractionHint._is_money(l[0]) else max(l)
        else:
            return None
