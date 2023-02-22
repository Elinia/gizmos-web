from enum import Enum, auto
from typing import Literal


class BuildMethod(Enum):
    DIRECTLY = auto()
    FROM_RESEARCH = auto()
    FROM_FILED = auto()


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


class Stage(Enum):
    MAIN = auto()
    RESEARCH = auto()
    TRIGGER = auto()
    EXTRA_PICK = auto()
    EXTRA_BUILD = auto()
    EXTRA_FILE = auto()
    EXTRA_RESEARCH = auto()
    GAME_OVER = auto()
