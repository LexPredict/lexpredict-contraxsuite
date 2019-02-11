from typing import List, Set, Generator, Union


def chunks(l: Union[Generator, List, Set], n: int):
    for i in range(0, len(l), n):
        yield l[i:i + n]
