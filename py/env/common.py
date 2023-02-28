from enum import Enum
from typing import Literal


class BuildMethod(str, Enum):
    DIRECTLY = 'DIRECTLY'
    FROM_RESEARCH = 'FROM_RESEARCH'
    FROM_FILED = 'FROM_FILED'


Energy = Literal['red', 'blue', 'black', 'yellow']

ALL_ENERGY_TYPES: list[Energy] = ['red', 'blue', 'black', 'yellow']
ALL_GIZMO_LEVELS = [0, 1, 2, 3]
GIZMO_LEVELS = [1, 2, 3]
ALL_BUILD_METHODS = [
    BuildMethod.DIRECTLY,
    BuildMethod.FROM_FILED,
    BuildMethod.FROM_RESEARCH,
]

AllGizmoLevel = Literal[0, 1, 2, 3]
GizmoLevel = Literal[1, 2, 3]
EnergyWithAny = Literal['red', 'blue', 'black', 'yellow', 'any']


class Stage(str, Enum):
    MAIN = 'MAIN'
    RESEARCH = 'RESEARCH'
    TRIGGER = 'TRIGGER'
    EXTRA_PICK = 'EXTRA_PICK'
    EXTRA_BUILD = 'EXTRA_BUILD'
    EXTRA_FILE = 'EXTRA_FILE'
    EXTRA_RESEARCH = 'EXTRA_RESEARCH'
    GAME_OVER = 'GAME_OVER'
