from __future__ import annotations
from enum import Enum
from typing import Literal, TypeGuard, TypedDict, TYPE_CHECKING

from common import GizmoLevel, EnergyWithAny, Energy, AllGizmoLevel, BuildMethod, Stage

if TYPE_CHECKING:
    from Player import Player


class GizmoType(str, Enum):
    PICK = 'PICK'
    BUILD = 'BUILD'
    UPGRADE = 'UPGRADE'
    CONVERTER = 'CONVERTER'
    FILE = 'FILE'


class NaEffect(TypedDict):
    type: Literal['na']


class FreeDrawEffect(TypedDict):
    type: Literal['free_draw']
    num: int


class FreePickEffect(TypedDict):
    type: Literal['free_pick']
    num: int


class AddPointTokenEffect(TypedDict):
    type: Literal['add_point_token']
    num: int


class ExtraFileEffect(TypedDict):
    type: Literal['extra_file']


class ExtraResearchEffect(TypedDict):
    type: Literal['extra_research']


class ExtraBuildEffect(TypedDict):
    type: Literal['extra_build']
    level: list[GizmoLevel]


class EnergyAsPointEffect(TypedDict):
    type: Literal['energy_as_point']


class TokenAsPointEffect(TypedDict):
    type: Literal['token_as_point']


Effect = NaEffect | FreeDrawEffect | FreePickEffect | AddPointTokenEffect | ExtraFileEffect | ExtraResearchEffect | ExtraBuildEffect | EnergyAsPointEffect | TokenAsPointEffect


class GizmoBasic(TypedDict):
    id: int
    level: AllGizmoLevel
    energy_type: EnergyWithAny
    energy_cost: int
    value: int
    effect: Effect | None


class GizmoInfo(TypedDict):
    id: int
    active: bool
    used: bool
    where: Literal['excluded', 'pool', 'board', 'research', 'file', 'player']
    belongs_to: int | None


class Gizmo:
    type: GizmoType
    id: int
    level: AllGizmoLevel
    energy_type: EnergyWithAny
    energy_cost: int
    value: int
    effect: Effect

    active: bool
    used: bool

    where: Literal['excluded', 'pool', 'board', 'research', 'file', 'player']
    belongs_to: int | None

    def assert_available(self):
        if not self.active:
            raise Exception('gizmo not activated')
        if self.used:
            raise Exception('gizmo used')

    def used_by(self, player: Player):
        self.assert_available()
        if self.effect['type'] == 'free_draw':
            self.free_draw(player, self.effect['num'])
        elif self.effect['type'] == 'free_pick':
            self.free_pick(player, self.effect['num'])
        elif self.effect['type'] == 'add_point_token':
            self.add_point_token(player, self.effect['num'])
        elif self.effect['type'] == 'extra_file':
            self.extra_file(player)
        elif self.effect['type'] == 'extra_research':
            self.extra_research(player)
        elif self.effect['type'] == 'extra_build':
            self.extra_build(player, self.effect['level'])
        self.active = False
        self.used = True

    def free_draw(self, player: Player, num: int):
        if player.env.energy_pool_len() <= 0:
            return
        draw_num = min(num, player.max_energy_num - player.total_energy_num)
        for energy in player.env.draw_energy_from_pool(draw_num):
            player.add_energy(energy)

    def free_pick(self, player: Player, num: int):
        if len(player.env.state['energy_board']) <= 0:
            return
        player.env.state['free_pick_num'] = num

    def add_point_token(self, player: Player, num: int):
        player.point_token += num

    def extra_file(self, player: Player):
        player.env.state['curr_stage'] = Stage.EXTRA_FILE

    def extra_research(self, player: Player):
        if player.research_num <= 0:
            return
        player.env.state['curr_stage'] = Stage.EXTRA_RESEARCH

    def extra_build(self, player: Player, level: list[GizmoLevel]):
        player.env.state['free_build'] = {'level': level}
        player.env.state['curr_stage'] = Stage.EXTRA_BUILD

    def reset_used(self):
        self.active = False
        self.used = False

    def reset(self):
        self.reset_used()
        self.where = 'excluded'
        self.belongs_to = None

    def get_value(self, player: Player):
        if self.effect['type'] == 'token_as_point':
            return player.point_token
        if self.effect['type'] == 'energy_as_point':
            return player.total_energy_num
        return self.value

    @property
    def info(self) -> GizmoInfo:
        return {
            'id': self.id,
            'active': self.active,
            'used': self.used,
            'where': self.where,
            'belongs_to': self.belongs_to,
        }

    def __init__(self, **basic: GizmoBasic):
        self.id = basic['id']
        self.level = basic['level']
        self.energy_type = basic['energy_type']
        self.energy_cost = basic['energy_cost']
        self.value = basic['value']
        self.effect = basic.get('effect', {'type': 'na'})

        self.active = False
        self.used = False

        self.where = 'excluded'
        self.belongs_to = None


class GizmoPick(TypedDict):
    when_pick: list[Energy]


class PickGizmo(Gizmo):
    type = GizmoType.PICK
    when_pick: list[Energy]

    def is_satisfied(self, energy: Energy) -> bool:
        return energy in self.when_pick

    def on_pick(self, energy: Energy):
        if not self.is_satisfied(energy):
            return
        if not self.used:
            self.active = True

    def __init__(self, when_pick: list[Energy], **basic: GizmoBasic):
        super().__init__(**basic)
        self.when_pick = when_pick


class WhenBuild(TypedDict):
    energy: list[Energy] | Literal['any']
    level: list[AllGizmoLevel] | Literal['any']
    method: list[BuildMethod] | Literal['any']


class GizmoBuild(TypedDict):
    when_build: WhenBuild


class BuildGizmo(Gizmo):
    type = GizmoType.BUILD
    when_build: WhenBuild

    def is_satisfied(self, player: Player, level: GizmoLevel, energy: EnergyWithAny, method: BuildMethod) -> bool:
        return (
            (self.when_build['level'] == 'any' or level in self.when_build['level']) and
            (self.when_build['energy'] == 'any' or energy == 'any' or energy in self.when_build['energy']) and
            (self.when_build['method'] == 'any' or method in self.when_build['method']) and
            (self.effect['type'] != 'extra_file' or player.can_file) and
            (self.effect['type'] != 'extra_research' or player.can_research)
        )

    def on_build(self, player: Player, level: GizmoLevel, energy: EnergyWithAny, method: BuildMethod):
        if not self.is_satisfied(player, level, energy, method):
            return
        if not self.used:
            self.active = True

    def __init__(self, when_build: WhenBuild, **basic: GizmoBasic):
        super().__init__(**basic)
        self.when_build = when_build


class GizmoUpgrade(TypedDict):
    max_energy_num: int | None
    max_file_num: int | None
    research_num: int | None
    build_from_filed_cost_reduction: int | None
    build_from_research_cost_reduction: int | None


class UpgradeGizmo(Gizmo):
    type = GizmoType.UPGRADE
    max_energy_num: int
    max_file_num: int
    research_num: int
    build_from_filed_cost_reduction: int
    build_from_research_cost_reduction: int

    def __init__(self, **basic: GizmoBasic & GizmoUpgrade):
        super().__init__(**basic)
        self.max_energy_num = basic.get('max_energy_num', 0)
        self.max_file_num = basic.get('max_file_num', 0)
        self.research_num = basic.get('research_num', 0)
        self.build_from_filed_cost_reduction = basic.get(
            'build_from_filed_cost_reduction', 0)
        self.build_from_research_cost_reduction = basic.get(
            'build_from_research_cost_reduction', 0)


class FormulaSide(TypedDict):
    energy: EnergyWithAny
    num: int


ConverterFormula = dict[Literal['from', 'to'], FormulaSide]


class Prerequisite(TypedDict):
    level: list[AllGizmoLevel]


class GizmoConverter(TypedDict):
    prerequisite: Prerequisite | None
    formulae: list[ConverterFormula]


class ConverterGizmo(Gizmo):
    type = GizmoType.CONVERTER
    prerequisite: Prerequisite | None
    formulae: list[ConverterFormula]

    def is_satisfied(self, gizmo: Gizmo) -> bool:
        return (
            not self.used and
            (not self.prerequisite or gizmo.level in self.prerequisite['level'])
        )

    def on_convert(self, gizmo: Gizmo):
        if not self.is_satisfied(gizmo):
            return
        self.active = True

    def __init__(self, **basic: GizmoBasic & GizmoConverter):
        super().__init__(**basic)
        self.prerequisite = basic.get('prerequisite')
        self.formulae = basic['formulae']


class FileGizmo(Gizmo):
    type = GizmoType.FILE

    def on_file(self):
        if not self.used:
            self.active = True

    def __init__(self, **basic: GizmoBasic):
        super().__init__(**basic)


def is_upgrade_gizmo(gizmo: Gizmo) -> TypeGuard[UpgradeGizmo]:
    return isinstance(gizmo, UpgradeGizmo)


def is_converter_gizmo(gizmo: Gizmo) -> TypeGuard[ConverterGizmo]:
    return isinstance(gizmo, ConverterGizmo)


def is_pick_gizmo(gizmo: Gizmo) -> TypeGuard[PickGizmo]:
    return isinstance(gizmo, PickGizmo)


def is_build_gizmo(gizmo: Gizmo) -> TypeGuard[BuildGizmo]:
    return isinstance(gizmo, BuildGizmo)


def is_file_gizmo(gizmo: Gizmo) -> TypeGuard[FileGizmo]:
    return isinstance(gizmo, FileGizmo)
