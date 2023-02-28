import math
import random
import functools
from typing import Callable, TypeVar


def random_int(max: int):
    return math.floor(random.random() * max)


T = TypeVar("T")


def proper_subsets(arr: list[T]):
    subsets: list[list[T]] = [[]]
    for v in arr:
        new_subsets = [subset + [v] for subset in subsets]
        subsets = subsets + new_subsets
    return [subset for subset in subsets if len(subset) > 0]


def sample(arr: list[T]):
    return arr[random_int(len(arr))]


def compose(a: list[list[T]], b: list[T]) -> list[list[T]]:
    res = []
    for _a in a:
        for _b in b:
            res.append(_a + [_b])
    return res


def list_compose(list: list[list[T]]):
    return functools.reduce(lambda acc, curr: compose(acc, curr), list, [[]])


def find_index(src: list[T], func: Callable[[T], bool]):
    for i, v in enumerate(src):
        if func(v):
            return i
    return -1
