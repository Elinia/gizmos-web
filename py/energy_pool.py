from random import shuffle

from common import Energy

ENERGY_POOL: list[Energy] = ['red']*13 + \
    ['yellow']*13 + ['blue']*13 + ['black']*13


def init_energy_pool() -> list[Energy]:
    E = list(ENERGY_POOL)
    shuffle(E)
    return E
