from random import shuffle
from typing import List

from common import Energy

ENERGY_POOL: List[Energy] = ['red']*13 + \
    ['yellow']*13 + ['blue']*13 + ['black']*13


def init_energy_pool() -> List[Energy]:
    E = list(ENERGY_POOL)
    shuffle(E)
    return E
