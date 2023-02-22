from __future__ import annotations
from typing import TypedDict, TYPE_CHECKING
from random import shuffle, choice
from enum import Enum, auto
from gymnasium import Env

from Player import Player, PlayerInfo
from gizmos_pool import init_gizmos
from energy_pool import init_energy_pool
from common import ALL_ENERGY_TYPES, BuildMethod, Stage, Energy, GizmoLevel
from utils import find_index

if TYPE_CHECKING:
    from Gizmo import Gizmo, GizmoInfo

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

    class Observation(TypedDict):
        curr_turn: int
        curr_stage: Stage
        curr_player_index: int
        is_last_turn: bool
        energy_pool_num: int
        energy_board: list[Energy]
        gizmos_pool_num: dict[GizmoLevel, int]
        gizmos_board: dict[GizmoLevel, list[GizmoInfo]]
        researching: ResearchingInfo
        players: list[PlayerInfo]
        free_build: State.free_build
        free_pick_num: State.free_pick_num
        truncated: bool
        action_space: list[Action]


def init_player(env: GizmosEnv, index: int):
    return Player(env=env, index=index, gizmos=[env.u_gizmo(index)])


class ActionType(Enum):
    PICK = auto()
    FILE = auto()
    FILE_FROM_RESEARCH = auto()
    BUILD = auto()
    BUILD_FROM_RESEARCH = auto()
    BUILD_FROM_FILED = auto()
    BUILD_FOR_FREE = auto()
    RESEARCH = auto()
    CHOOSE_TRIGGER = auto()
    USE_GIZMO = auto()
    GIVE_UP = auto()
    END = auto()


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


class ChooseTriggerAction(TypedDict):
    type: ActionType.CHOOSE_TRIGGER
    gizmos: list[int]


class UseGizmoAction(TypedDict):
    type: ActionType.USE_GIZMO
    id: int


class GiveUpAction(TypedDict):
    type: ActionType.GIVE_UP


class EndAction(TypedDict):
    type: ActionType.END


Action = PickAction | FileAction | FileFromResearchAction | BuildAction | BuildFromFileAction | BuildFromResearchAction | BuildForFreeAction | ResearchAction | ChooseTriggerAction | UseGizmoAction | GiveUpAction | EndAction


class GizmosEnv(Env):
    def __init__(self, player_num=2, max_gizmos_num=16, max_level3_gizmos_num=4, check=True, log=True):
        if player_num < 1 or max_gizmos_num < 2 or max_level3_gizmos_num < 1:
            raise ValueError('unsupported configuration')
        self.check = check
        self.log = log
        self.player_num = player_num
        self.max_gizmos_num = max_gizmos_num
        self.max_level3_gizmos_num = max_level3_gizmos_num
        self.reset()
        # self.action_space = spaces.Discrete(len(ActionType))
        # self.observation_space = spaces.Dict({
        #     'curr_turn': spaces.Discrete(self.state['curr_turn']),
        #     'curr_stage': spaces.Discrete(self.state['curr_stage']),
        #     'curr_player_index': spaces.Discrete(self.state['curr_player_index']),
        #     'is_last_turn': spaces.Discrete(self.state['is_last_turn']),
        #     'energy_pool_num': spaces.Discrete(self.energy_pool_len()),
        #     'energy_board': spaces.Discrete(self.state['energy_board']),
        #     'gizmos_pool_num': spaces.Dict({
        #         1: spaces.Discrete(self.gizmos_pool_len(1)),
        #         2: spaces.Discrete(self.gizmos_pool_len(2)),
        #         3: spaces.Discrete(self.gizmos_pool_len(3)),
        #     }),
        #     'gizmos_board': spaces.Dict({
        #         1: spaces.Discrete(self.state['gizmos_board'][1].map(g => g.info)),
        #         2: spaces.Discrete(self.state['gizmos_board'][2].map(g => g.info)),
        #         3: spaces.Discrete(self.state['gizmos_board'][3].map(g => g.info)),
        #     }),
        #     'researching': spaces.Dict({
        #         'level': spaces.Discrete(self.state['researching'].level),
        #         'gizmos': spaces.Discrete(self.state['researching'].gizmos.map(g => g.info)),
        #     }),
        #     'players': spaces.Discrete(self.state['players'].map(p => p.info)),
        #     'free_build': spaces.Discrete(self.state['free_build']),
        #     'free_pick_num': spaces.Discrete(self.state['free_pick_num']),
        #     'truncated': spaces.Discrete(self.truncated),
        # })

    def reset(self):
        self.truncated = False
        self.state: State = {
            'curr_turn': 1,
            'curr_stage': Stage.MAIN,
            'curr_player_index': 0,
            'is_last_turn': False,
            'energy_pool': init_energy_pool(),
            'energy_board': [],
            **init_gizmos(),
            'gizmos_board': {
                1: [],
                2: [],
                3: [],
            },
            'players': [],
            'researching': None,
            'free_build': None,
            'free_pick_num': 0,
        }
        self.state['energy_board'] = self.draw_energy_from_pool(6)
        self.state['gizmos_board'][1] = self.draw_gizmos_from_pool(1, 4)
        self.state['gizmos_board'][2] = self.draw_gizmos_from_pool(2, 3)
        self.state['gizmos_board'][3] = self.draw_gizmos_from_pool(3, 2)
        for i in range(self.player_num):
            self.state['players'].append(init_player(self, i))

    def draw_gizmos_from_pool(self, level: GizmoLevel, num: int):
        _len = len(self.state['gizmos_pool'][level])
        gizmos = self.state['gizmos_pool'][level][:min(num, _len)]
        del self.state['gizmos_pool'][level][:min(num, _len)]
        return gizmos

    def drop_gizmos_to_pool(self, level: GizmoLevel, gizmos: list[Gizmo]):
        self.state['gizmos_pool'][level] += gizmos
        shuffle(self.state['gizmos_pool'][level])

    def pick_gizmo_from_board(self, id: int):
        gizmo = next(g for g in self.all_board_gizmos if g.id == id)
        if not gizmo:
            raise ValueError('[pick_gizmo_from_board] no such gizmo')
        self.state['gizmos_board'][gizmo.level] = [
            *filter(lambda g: g.id != id,
                    self.state['gizmos_board'][gizmo.level]),
            *self.draw_gizmos_from_pool(gizmo.level, 1),
        ]
        return gizmo

    def draw_energy_from_pool(self, num: int):
        _len = len(self.state['energy_pool'])
        energy = self.state['energy_pool'][:min(num, _len)]
        del self.state['energy_pool'][:min(num, _len)]
        return energy

    def drop_energy_to_pool(self, energy_num: dict[Energy, int]):
        energy_list = []
        for energy in ALL_ENERGY_TYPES:
            energy_list += [energy]*energy_num[energy]
        self.state['energy_pool'] += energy_list
        shuffle(self.state['energy_pool'])

    def pick_energy_from_board(self, energy: Energy):
        try:
            index = self.state['energy_board'].index(energy)
        except ValueError:
            raise Exception('[pick_energy_from_board] no such energy')
        self.state['energy_board'].pop(index)
        self.state['energy_board'] = self.state['energy_board'] + \
            self.draw_energy_from_pool(1)
        return energy

    def pick_gizmo_from_research(self, id: int):
        researching = self.state['researching']
        if not researching:
            raise Exception('[pick_gizmo_from_research] not researching')
        index = find_index(researching['gizmos'], lambda g: g.id == id)
        if index == -1:
            raise Exception('[pick_gizmo_from_research] no such gizmo')
        gizmo = researching['gizmos'].pop(index)
        self.drop_gizmos_to_pool(researching['level'], researching['gizmos'])
        self.state['researching'] = None
        return gizmo

    def gizmos_pool_len(self, level: GizmoLevel):
        return len(self.state['gizmos_pool'][level])

    def energy_pool_len(self):
        return len(self.state['energy_pool'])

    @property
    def curr_player(self):
        return self.state['players'][self.state['curr_player_index']]

    @property
    def avail_actions(self):
        actions: set[Action] = set()
        if self.state['curr_stage'] == Stage.MAIN:
            actions.add(ActionType.END)
            if len(self.state['energy_board']) > 0:
                actions.add(ActionType.PICK)
            if len(self.buildable_gizmos(self.all_board_gizmos, BuildMethod.DIRECTLY)) > 0:
                actions.add(ActionType.BUILD)
            if self.curr_player.research_num > 0:
                actions.add(ActionType.RESEARCH)
            if len(self.curr_player.filed) < self.curr_player.max_file_num:
                actions.add(ActionType.FILE)
            if len(self.curr_player.filed) > 0 and len(self.buildable_gizmos(self.curr_player.filed, BuildMethod.FROM_FILED)) > 0:
                actions.add(ActionType.BUILD_FROM_FILED)
        elif self.state['curr_stage'] == Stage.RESEARCH:
            actions.add(ActionType.GIVE_UP)
            if len(self.buildable_gizmos(self.state['researching']['gizmos'], BuildMethod.FROM_RESEARCH)) > 0:
                actions.add(ActionType.BUILD_FROM_RESEARCH)
            if len(self.curr_player.filed) < self.curr_player.max_file_num:
                actions.add(ActionType.FILE_FROM_RESEARCH)
        elif self.state['curr_stage'] == Stage.TRIGGER:
            actions.add(ActionType.END)
            if len(self.curr_player.avail_gizmos) > 0:
                actions.add(ActionType.USE_GIZMO)
        elif self.state['curr_stage'] == Stage.EXTRA_PICK:
            actions.add(ActionType.GIVE_UP)
            if len(self.state['energy_board']) > 0:
                actions.add(ActionType.PICK)
        elif self.state['curr_stage'] == Stage.EXTRA_BUILD:
            actions.add(ActionType.GIVE_UP)
            if self.state['free_build']:
                actions.add(ActionType.BUILD_FOR_FREE)
            elif len(self.buildable_gizmos(self.all_board_gizmos, BuildMethod.DIRECTLY)) > 0:
                actions.add(ActionType.BUILD)
        elif self.state['curr_stage'] == Stage.EXTRA_FILE:
            actions.add(ActionType.GIVE_UP)
            if len(self.curr_player.filed) < self.curr_player.max_file_num:
                actions.add(ActionType.FILE)
        elif self.state['curr_stage'] == Stage.EXTRA_RESEARCH:
            actions.add(ActionType.GIVE_UP)
            if self.curr_player.research_num > 0:
                actions.add(ActionType.RESEARCH)
        elif self.state['curr_stage'] == Stage.GAME_OVER:
            pass
        else:
            raise Exception('[avail_actions] unexpected stage')
        return actions

    def action_avail(self, action: Action):
        if not self.check:
            return True
        return action in self.avail_actions

    def pick(self, energy: Energy):
        self.pick_energy_from_board(energy)
        self.curr_player.pick(energy)
        self.state['curr_stage'] = Stage.TRIGGER

    def file(self, id: int):
        gizmo = self.pick_gizmo_from_board(id)
        self.curr_player.file(gizmo)
        self.state['curr_stage'] = Stage.TRIGGER

    def file_from_research(self, id: int):
        gizmo = self.pick_gizmo_from_research(id)
        self.curr_player.file(gizmo)
        self.state['curr_stage'] = Stage.TRIGGER

    def build(self, id: int, cost_energy_num: dict[Energy, int], cost_converter_gizmos_id: list[int]):
        gizmo = self.pick_gizmo_from_board(id)
        self.curr_player.build(gizmo, cost_energy_num,
                               cost_converter_gizmos_id)
        self.state['curr_stage'] = Stage.TRIGGER

    def build_from_filed(self, id: int, cost_energy_num: dict[Energy, int], cost_converter_gizmos_id: list[int]):
        self.curr_player.build_from_filed(
            id, cost_energy_num, cost_converter_gizmos_id)
        self.state['curr_stage'] = Stage.TRIGGER

    def build_from_research(self, id: int, cost_energy_num: dict[Energy, int], cost_converter_gizmos_id: list[int]):
        gizmo = self.pick_gizmo_from_research(id)
        self.curr_player.build_from_research(
            gizmo, cost_energy_num, cost_converter_gizmos_id)
        self.state['curr_stage'] = Stage.TRIGGER

    def build_for_free(self, id: int):
        if not self.state['free_build']:
            raise Exception('[build_for_free] no free build')
        gizmo = self.pick_gizmo_from_board(id)
        if not self.state['free_build'].level.includes(gizmo.level):
            raise Exception('[build_for_free] wrong level')
        self.curr_player.build_for_free(gizmo)
        self.state['free_build'] = None
        self.state['curr_stage'] = Stage.TRIGGER

    def research(self, level: GizmoLevel):
        self.state['researching'] = {
            'level': level,
            'gizmos': self.draw_gizmos_from_pool(level, self.curr_player.research_num),
        }
        self.state['curr_stage'] = Stage.RESEARCH

    def give_up(self):
        if self.state['curr_stage'] == Stage.EXTRA_PICK:
            self.state['free_pick_num'] = 0
        elif self.state['curr_stage'] == Stage.EXTRA_BUILD:
            if self.state['free_build']:
                self.state['free_build'] = None
        elif self.state['curr_stage'] == Stage.EXTRA_FILE:
            pass
        elif self.state['curr_stage'] == Stage.EXTRA_RESEARCH:
            pass
        elif self.state['curr_stage'] == Stage.RESEARCH:
            if not self.state['researching']:
                raise Exception('[give_up] no researching')
            self.drop_gizmos_to_pool(
                self.state['researching']['level'], self.state['researching']['gizmos'])
            self.state['researching'] = None
        else:
            raise Exception('[give_up] unexpected stage')
        self.state['curr_stage'] = Stage.TRIGGER

    def use_gizmo(self, id: int):
        if not self.action_avail(ActionType.USE_GIZMO):
            raise Exception('[use_gizmo] unavailable')
        self.curr_player.use_gizmo(id)

    def next_player(self):
        if len(self.curr_player.gizmos) >= self.max_gizmos_num or len(self.curr_player.level3_gizmos) >= self.max_level3_gizmos_num:
            self.state['is_last_turn'] = True
        if self.state['curr_player_index'] + 1 >= len(self.state['players']):
            if self.state['is_last_turn']:
                self.state['curr_stage'] = Stage.GAME_OVER
                return
        self.curr_player.reset_gizmos()
        self.state['curr_player_index'] = (
            self.state['curr_player_index'] + 1) % len(self.state['players'])
        self.state['curr_turn'] += 1
        self.state['curr_stage'] = Stage.MAIN

    def game_over(self):
        if self.log:
            print('game over')
            print('turn:', self.state['curr_turn'])
            for player in self.state['players']:
                print(player.score)
        return

    # def get_reward(self, playerIndex):
    #     if self.state['curr_stage'] != Stage.GAME_OVER:
    #         return 0
    #     if self.truncated:
    #         return float('-inf')
    #     score = self.state['players'][playerIndex].score
    #     rank = len(
    #         list(filter(lambda player: player.score > score, self.state['players']))) + 1
    #     winner_reward = ((1 + self.player_num) * self.player_num) / 2
    #     loser_reward = 1 - rank
    #     return winner_reward if rank == 1 else loser_reward

    def step(self, playerIndex: int, action: Action):
        if self.log:
            print('[step]', playerIndex, action)
        try:
            if playerIndex != self.state['curr_player_index']:
                print('[step] not your turn')
                return
            if not self.action_avail(action['type']):
                print('[step] action {} unavailable'.format(action['type']))
                return
            if action['type'] == ActionType.PICK:
                self.pick(action['energy'])
            elif action['type'] == ActionType.FILE:
                self.file(action['id'])
            elif action['type'] == ActionType.FILE_FROM_RESEARCH:
                self.file_from_research(action['id'])
            elif action['type'] == ActionType.BUILD:
                self.build(
                    action['id'],
                    action['cost_energy_num'],
                    action['cost_converter_gizmos_id'])
            elif action['type'] == ActionType.BUILD_FROM_FILED:
                self.build_from_filed(
                    action['id'],
                    action['cost_energy_num'],
                    action['cost_converter_gizmos_id'])
            elif action['type'] == ActionType.BUILD_FROM_RESEARCH:
                self.build_from_research(
                    action['id'],
                    action['cost_energy_num'],
                    action['cost_converter_gizmos_id'])
            elif action['type'] == ActionType.BUILD_FOR_FREE:
                self.build_for_free(action['id'])
            elif action['type'] == ActionType.RESEARCH:
                self.research(action['level'])
            elif action['type'] == ActionType.USE_GIZMO:
                self.use_gizmo(action['id'])
            elif action['type'] == ActionType.GIVE_UP:
                self.give_up()
            elif action['type'] == ActionType.END:
                self.next_player()
            else:
                print('[step] unexpected action type')
                return
            if self.state['free_pick_num'] > 0 and self.curr_player.can_add_energy:
                self.state['free_pick_num'] -= 1
                self.state['curr_stage'] = Stage.EXTRA_PICK
            else:
                self.state['free_pick_num'] = 0
                if all(map(lambda a: a == ActionType.END, self.avail_actions)):
                    self.next_player()
            if self.state['curr_stage'] == Stage.GAME_OVER:
                self.game_over()
        except Exception as e:
            print(e)
            self.truncated = True
            self.state['curr_stage'] = Stage.GAME_OVER

    def u_gizmo(self, id: int):
        return self.state['gizmos'][id]

    def gizmo(self, id: int):
        gizmo = self.u_gizmo(id)
        if gizmo.level == 0:
            raise Exception('unexpected gizmo')
        return gizmo

    def observation(self, playerIndex: int | None = None) -> Observation:
        is_curr_player = playerIndex == self.state['curr_player_index']
        return {
            'curr_turn': self.state['curr_turn'],
            'curr_stage': self.state['curr_stage'],
            'curr_player_index': self.state['curr_player_index'],
            'is_last_turn': self.state['is_last_turn'],
            'energy_pool_num': self.energy_pool_len(),
            'energy_board': self.state['energy_board'],
            'gizmos_pool_num': {
                1: self.gizmos_pool_len(1),
                2: self.gizmos_pool_len(2),
                3: self.gizmos_pool_len(3),
            },
            'gizmos_board': {
                1: [g.info for g in self.state['gizmos_board'][1]],
                2: [g.info for g in self.state['gizmos_board'][2]],
                3: [g.info for g in self.state['gizmos_board'][3]],
            },
            'researching': {
                'level': self.state['researching']['level'],
                'gizmos': [g.info for g in self.state['researching']['gizmos']]
            } if is_curr_player and self.state['researching'] is not None else None,
            'players': [p.info for p in self.state['players']],
            'free_build': self.state['free_build'],
            'free_pick_num': self.state['free_pick_num'],
            'truncated': self.truncated,
            'action_space': self.action_space,
        }

    def build_solutions(self, gizmo_like: Gizmo | int, method: BuildMethod, check_only: bool = False):
        player = self.curr_player
        gizmo = self.gizmo(gizmo_like) if type(
            gizmo_like) == int else gizmo_like

        return player.build_solutions(
            gizmo,
            method,
            player.energy_num,
            [g for g in player.converter_gizmos if g.is_satisfied(gizmo)],
            check_only
        )

    def can_build(self, gizmo: Gizmo, method: BuildMethod):
        return len(self.build_solutions(gizmo, method, True)) > 0

    def buildable_gizmos(self, gizmos: list[Gizmo] | set[Gizmo], method: BuildMethod):
        return [g for g in gizmos if self.can_build(g, method)]

    @property
    def all_board_gizmos(self):
        return self.state['gizmos_board'][1] + self.state['gizmos_board'][2] + self.state['gizmos_board'][3]

    def space_pick(self) -> list[PickAction]:
        if self.state['curr_stage'] not in [Stage.MAIN, Stage.EXTRA_PICK]:
            return []
        if not self.curr_player.can_add_energy:
            return []
        return [{
            'type': ActionType.PICK,
            'energy': energy,
        } for energy in self.state['energy_board']]

    def space_file(self) -> list[FileAction]:
        if self.state['curr_stage'] not in [Stage.MAIN, Stage.EXTRA_FILE]:
            return []
        if not self.curr_player.can_file:
            return []
        return [{
            'type': ActionType.FILE,
            'id': gizmo.id,
        } for gizmo in self.all_board_gizmos]

    def space_file_from_research(self) -> list[FileFromResearchAction]:
        if self.state['curr_stage'] != Stage.RESEARCH:
            return []
        researching = self.state['researching']
        if not researching:
            return []
        if not self.curr_player.can_file:
            return []
        return [{
            'type': ActionType.FILE_FROM_RESEARCH,
            'id': gizmo.id,
        } for gizmo in researching['gizmos']]

    def space_build(self, gizmos: list[Gizmo], method: BuildMethod, action_type: ActionType) -> list[BuildAction | BuildFromFileAction | BuildFromResearchAction]:
        actions = []
        for gizmo in gizmos:
            for solution in self.build_solutions(gizmo, method):
                actions.append({
                    'type': action_type,
                    'id': gizmo.id,
                    'cost_energy_num': solution['energy_num'],
                    'cost_converter_gizmos_id': [g.id for g in solution['gizmos']],
                })
        return actions

    def space_build_directly(self) -> list[BuildAction]:
        if self.state['curr_stage'] not in [Stage.MAIN, Stage.EXTRA_BUILD]:
            return []
        return self.space_build(
            self.all_board_gizmos,
            BuildMethod.DIRECTLY,
            ActionType.BUILD,
        )

    def space_build_from_file(self) -> list[BuildFromFileAction]:
        if self.state['curr_stage'] != Stage.MAIN:
            return []
        return self.space_build(
            self.curr_player.filed,
            BuildMethod.FROM_FILED,
            ActionType.BUILD_FROM_FILED,
        )

    def space_build_from_research(self) -> list[BuildFromResearchAction]:
        if self.state['curr_stage'] != Stage.RESEARCH:
            return []
        researching_gizmos = self.state['researching']['gizmos'] if self.state['researching'] else [
        ]
        return self.space_build(
            researching_gizmos,
            BuildMethod.FROM_RESEARCH,
            ActionType.BUILD_FROM_RESEARCH,
        )

    def space_build_for_free(self) -> list[BuildForFreeAction]:
        if self.state['curr_stage'] != Stage.EXTRA_BUILD:
            return []
        levels = self.state['free_build']['level'] if self.state['free_build'] else [
        ]
        avail_gizmos = [
            gizmo for level in levels for gizmo in self.state['gizmos_board'][level]]
        return [{
            'type': ActionType.BUILD_FOR_FREE,
            'id': gizmo.id,
        } for gizmo in avail_gizmos]

    def space_research(self) -> list[ResearchAction]:
        if self.state['curr_stage'] not in [Stage.MAIN, Stage.EXTRA_RESEARCH]:
            return []
        if self.curr_player.research_num <= 0:
            return []
        levels = [1, 2, 3]
        avail_levels = [level for level in levels if len(
            self.state['gizmos_pool'][level]) > 0]
        return [{
            'type': ActionType.RESEARCH,
            'level': level,
        } for level in avail_levels]

    def space_use_gizmo(self) -> list[UseGizmoAction]:
        if self.state['curr_stage'] != Stage.TRIGGER:
            return []
        return [{
            'type': ActionType.USE_GIZMO,
            'id': gizmo.id,
        } for gizmo in self.curr_player.avail_gizmos]

    def space_give_up(self) -> list[GiveUpAction]:
        if self.state['curr_stage'] not in [
            Stage.EXTRA_PICK,
            Stage.EXTRA_BUILD,
            Stage.EXTRA_FILE,
            Stage.EXTRA_RESEARCH,
            Stage.RESEARCH,
        ]:
            return []
        return [{'type': ActionType.GIVE_UP}]

    def space_end(self) -> list[EndAction]:
        if self.state['curr_stage'] not in [Stage.MAIN, Stage.TRIGGER]:
            return []
        return [{'type': ActionType.END}]

    @property
    def action_space(self) -> list[Action]:
        return [
            *self.space_pick(),
            *self.space_file(),
            *self.space_file_from_research(),
            *self.space_build_directly(),
            *self.space_build_from_file(),
            *self.space_build_from_research(),
            *self.space_build_for_free(),
            *self.space_research(),
            *self.space_use_gizmo(),
            *self.space_give_up(),
            *self.space_end(),
        ]

    def sample(self):
        return choice(self.action_space)
