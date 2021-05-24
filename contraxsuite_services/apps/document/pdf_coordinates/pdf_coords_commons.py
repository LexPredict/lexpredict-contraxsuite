from enum import Enum
from typing import Tuple

XYWH = Tuple[float, float, float, float]

XminYminXmaxYmax = Tuple[float, float, float, float]


class Dir(Enum):
    vertical = 0
    horizontal = 1


class SelectionArea:
    def __init__(self, page: int, area: XYWH):
        self.area = area
        self.page = page

    def __str__(self):
        if not self.area:
            return 'empty'
        x, y, w, h = self.area
        return f'[x:{x}, y:{y}, w:{w}, h:{h}], page={self.page}'

    def __repr__(self):
        return self.__str__()
