import math
import random
import functools
from typing import List


def random_int(max: int):
    return math.floor(random.random() * max)


def proper_subsets(arr: List):
    subsets = [[]]
    for v in arr:
        new_subsets = [subset + [v] for subset in subsets]
        subsets = subsets + new_subsets
    return [subset for subset in subsets if len(subset) > 0]


def sample(arr: List):
    return arr[random_int(len(arr))]


def compose(a, b):
    res = []
    for _a in a:
        for _b in b:
            res.append(_a + [_b])
    return res


def list_compose(list: List):
    return functools.reduce(lambda acc, curr: compose(acc, curr), list, [[]])


def find_index(src: List, func):
    for i, v in enumerate(src):
        if func(v):
            return i
    return -1
