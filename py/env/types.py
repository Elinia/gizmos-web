
from enum import Enum
from typing import TypedDict
from .Gizmo import Gizmo, GizmoInfo
from .Player import Player, PlayerInfo
from .common import Energy, GizmoLevel, Stage


class Researching(TypedDict):
    level: GizmoLevel
    gizmos: list[Gizmo]


class FreeBuild(TypedDict):
    level: list[GizmoLevel]


class State(TypedDict):
    curr_turn: int
    curr_stage: Stage
    curr_player_index: int
    is_last_turn: bool
    energy_pool: list[Energy]
    energy_board: list[Energy]
    gizmos: list[Gizmo]
    gizmos_pool: dict[GizmoLevel, list[Gizmo]]
    gizmos_board: dict[GizmoLevel, list[Gizmo]]
    players: list[Player]
    researching: None | Researching
    free_build: None | FreeBuild
    free_pick_num: int


class ResearchingInfo(TypedDict):
    level: GizmoLevel
    gizmos: list[GizmoInfo]


class ActionType(str, Enum):
    PICK = 'PICK'
    FILE = 'FILE'
    FILE_FROM_RESEARCH = 'FILE_FROM_RESEARCH'
    BUILD = 'BUILD'
    BUILD_FROM_RESEARCH = 'BUILD_FROM_RESEARCH'
    BUILD_FROM_FILED = 'BUILD_FROM_FILED'
    BUILD_FOR_FREE = 'BUILD_FOR_FREE'
    RESEARCH = 'RESEARCH'
    USE_GIZMO = 'USE_GIZMO'
    GIVE_UP = 'GIVE_UP'
    END = 'END'

    def __str__(self) -> str:
        return self.value


class PickAction(TypedDict):
    type: ActionType.PICK
    energy: Energy


class FileAction(TypedDict):
    type: ActionType.FILE
    id: int


class FileFromResearchAction(TypedDict):
    type: ActionType.FILE_FROM_RESEARCH
    id: int


class ActionBuildSolution(TypedDict):
    id: int
    cost_energy_num: dict[Energy, int]
    cost_converter_gizmos_id: list[int]


class BuildAction(TypedDict):
    type: ActionType.BUILD
    id: int
    cost_energy_num: dict[Energy, int]
    cost_converter_gizmos_id: list[int]


class BuildFromFileAction(TypedDict):
    type: ActionType.BUILD_FROM_FILED
    id: int
    cost_energy_num: dict[Energy, int]
    cost_converter_gizmos_id: list[int]


class BuildFromResearchAction(TypedDict):
    type: ActionType.BUILD_FROM_RESEARCH
    id: int
    cost_energy_num: dict[Energy, int]
    cost_converter_gizmos_id: list[int]


class BuildForFreeAction(TypedDict):
    type: ActionType.BUILD_FOR_FREE
    id: int


class ResearchAction(TypedDict):
    type: ActionType.RESEARCH
    id: GizmoLevel


class UseGizmoAction(TypedDict):
    type: ActionType.USE_GIZMO
    id: int


class GiveUpAction(TypedDict):
    type: ActionType.GIVE_UP


class EndAction(TypedDict):
    type: ActionType.END


Action = PickAction | FileAction | FileFromResearchAction | BuildAction | BuildFromFileAction | BuildFromResearchAction | BuildForFreeAction | ResearchAction | UseGizmoAction | GiveUpAction | EndAction


class Observation(TypedDict):
    gizmos: list[GizmoInfo]
    curr_turn: int
    curr_stage: Stage
    curr_player_index: int
    is_last_turn: bool
    energy_pool_num: int
    energy_board: list[Energy]
    gizmos_pool_num: dict[GizmoLevel, int]
    gizmos_board: dict[GizmoLevel, list[GizmoInfo]]
    players: list[PlayerInfo]
    researching: None | ResearchingInfo
    free_build: None | FreeBuild
    free_pick_num: int
    truncated: bool
    action_space: list[Action]
    result: None | list[int]
