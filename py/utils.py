import math
import random
import functools
from typing import List, TypeVar


def random_int(max: int):
    return math.floor(random.random() * max)


T = TypeVar("T")


def proper_subsets(arr: List[T]):
    subsets: List[List[T]] = [[]]
    for v in arr:
        new_subsets = [subset + [v] for subset in subsets]
        subsets = subsets + new_subsets
    return [subset for subset in subsets if len(subset) > 0]


def sample(arr: List):
    return arr[random_int(len(arr))]


def compose(a: List[List[T]], b: List[T]) -> List[List[T]]:
    res = []
    for _a in a:
        for _b in b:
            res.append(_a + [_b])
    return res


def list_compose(list: List[List[T]]):
    return functools.reduce(lambda acc, curr: compose(acc, curr), list, [[]])


def find_index(src: List, func):
    for i, v in enumerate(src):
        if func(v):
            return i
    return -1
