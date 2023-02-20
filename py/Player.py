from __future__ import annotations
from typing import TYPE_CHECKING, Set, TypedDict, List, Dict, Optional
from gizmos_utils import init_energy_num
from common import ALL_ENERGY_TYPES, BuildMethod, Energy
from find_build_solutions import find_build_solutions
from Gizmo import Gizmo, GizmoInfo, is_upgrade_gizmo, is_converter_gizmo, is_pick_gizmo, is_build_gizmo, is_file_gizmo, GizmoType, Gizmo, BuildGizmo, ConverterGizmo, FileGizmo, PickGizmo, UpgradeGizmo

BASE_MAX_ENERGY = 5
BASE_MAX_FILE = 1
BASE_RESEARCH_NUM = 3

if TYPE_CHECKING:
    from GizmosEnv import GizmosEnv


def calc_total_energy_num(energy_num):
    return sum(energy_num.values())


class PlayerInfo(TypedDict):
    index: int
    gizmos: List[Gizmo]
    upgrade_gizmos: List[GizmoInfo]
    converter_gizmos: List[GizmoInfo]
    pick_gizmos: List[GizmoInfo]
    build_gizmos: List[GizmoInfo]
    file_gizmos: List[GizmoInfo]
    level3_gizmos: List[GizmoInfo]
    filed: List[GizmoInfo]
    point_token: int
    max_energy_num: int
    max_file_num: int
    research_num: int
    build_from_filed_cost_reduction: int
    build_from_research_cost_reduction: int
    energy_num: Dict[Energy, int]
    total_energy_num: int
    score: int


class Player:
    def __init__(self,
                 env: GizmosEnv,
                 index: int,
                 gizmos: Optional[List[Gizmo]] = None,
                 point_token: Optional[int] = None,
                 energy_num: Optional[Dict[Energy, int]] = None,
                 filed: Optional[List[Gizmo]] = None):
        self.env = env
        self.index = index
        self.max_energy_num = BASE_MAX_ENERGY
        self.max_file_num = BASE_MAX_FILE
        self.research_num = BASE_RESEARCH_NUM
        self.build_from_filed_cost_reduction = 0
        self.build_from_research_cost_reduction = 0
        self.gizmos: Set[Gizmo] = set()
        self.gizmos_by_type = {
            GizmoType.PICK: set(),
            GizmoType.BUILD: set(),
            GizmoType.UPGRADE: set(),
            GizmoType.CONVERTER: set(),
            GizmoType.FILE: set(),
        }
        for gizmo in gizmos or []:
            self.add_gizmo(gizmo)
        self.point_token = point_token or 0
        self.energy_num = energy_num or init_energy_num()
        self.filed = set([] if filed is None else filed)

    def add_energy(self, energy: Energy):
        if not self.can_add_energy:
            return
        self.energy_num[energy] += 1

    def add_gizmo(self, gizmo: Gizmo):
        self.gizmos.add(gizmo)
        if is_pick_gizmo(gizmo):
            self.gizmos_by_type[GizmoType.PICK].add(gizmo)
        elif is_build_gizmo(gizmo):
            self.gizmos_by_type[GizmoType.BUILD].add(gizmo)
        elif is_upgrade_gizmo(gizmo):
            self.gizmos_by_type[GizmoType.UPGRADE].add(gizmo)
            self.max_energy_num += gizmo.max_energy_num
            self.max_file_num += gizmo.max_file_num
            self.research_num += gizmo.research_num
            self.build_from_filed_cost_reduction += gizmo.build_from_filed_cost_reduction
            self.build_from_research_cost_reduction += gizmo.build_from_research_cost_reduction
        elif is_converter_gizmo(gizmo):
            self.gizmos_by_type[GizmoType.CONVERTER].add(gizmo)
        elif is_file_gizmo(gizmo):
            self.gizmos_by_type[GizmoType.FILE].add(gizmo)

    def pick_from_file(self, id: int):
        gizmo = self.env.gizmo(id)
        if gizmo not in self.filed:
            raise Exception("[pick_from_file] not in player's file")
        self.filed.remove(gizmo)
        return gizmo

    def pick(self, energy: Energy):
        self.add_energy(energy)
        for g in self.pick_gizmos:
            g.on_pick(energy)

    def file(self, gizmo: Gizmo):
        if not self.can_file:
            raise Exception('file overflow')
        self.filed.add(gizmo)
        for g in self.file_gizmos:
            g.on_file()

    def build(self, gizmo: Gizmo, cost_energy_num: Dict[Energy, int], cost_converter_gizmos_id: List[int], method=BuildMethod.DIRECTLY):
        converter_gizmos = [
            g for g in self.converter_gizmos if g.id in cost_converter_gizmos_id]
        if len(converter_gizmos) != len(cost_converter_gizmos_id):
            raise Exception('unexpected gizmo(s) used')

        if self.env.check and len(self.build_solutions(gizmo, method, cost_energy_num, converter_gizmos, True)) <= 0:
            raise Exception('no build solution')
        for g in converter_gizmos:
            g.on_convert(gizmo)
            g.used_by(self)
        self.drop(cost_energy_num)
        for g in self.build_gizmos:
            g.on_build(self, gizmo.level, gizmo.energy_type, method)
        self.add_gizmo(gizmo)

    def build_from_filed(self, id: int, cost_energy_num: Dict[Energy, int], cost_converter_gizmos_id: List[int]):
        gizmo = self.pick_from_file(id)
        self.build(gizmo, cost_energy_num,
                   cost_converter_gizmos_id, BuildMethod.FROM_FILED)

    def build_from_research(self, gizmo: Gizmo, cost_energy_num: Dict[Energy, int], cost_converter_gizmos_id: List[int]):
        self.build(gizmo, cost_energy_num, cost_converter_gizmos_id,
                   BuildMethod.FROM_RESEARCH)

    def build_for_free(self, gizmo: Gizmo):
        for g in self.build_gizmos:
            g.on_build(self, gizmo.level, gizmo.energy_type,
                       BuildMethod.DIRECTLY)
        self.add_gizmo(gizmo)

    def drop(self, energy_num: Dict[Energy, int]):
        for energy in ALL_ENERGY_TYPES:
            if self.energy_num[energy] < energy_num[energy]:
                raise Exception('not enough energy to drop')
            self.energy_num[energy] -= energy_num[energy]
        self.env.drop_energy_to_pool(energy_num)
        if self.total_energy_num > self.max_energy_num:
            raise Exception('energy overflow after drop')

    def use_gizmo(self, id: int):
        gizmo = self.env.u_gizmo(id)
        if gizmo not in self.gizmos:
            raise Exception("[use_gizmo] not in player's gizmos")
        self.env.state['gizmos'][id].used_by(self)

    def reset_gizmos(self):
        for g in self.gizmos:
            g.reset()

    @property
    def info(self) -> PlayerInfo:
        return {
            'index': self.index,
            'gizmos': [g.info for g in self.gizmos],
            'upgrade_gizmos': [g.info for g in self.upgrade_gizmos],
            'converter_gizmos': [g.info for g in self.converter_gizmos],
            'pick_gizmos': [g.info for g in self.pick_gizmos],
            'build_gizmos': [g.info for g in self.build_gizmos],
            'file_gizmos': [g.info for g in self.file_gizmos],
            'level3_gizmos': [g.info for g in self.level3_gizmos],
            'filed': [g.info for g in self.filed],
            'point_token': self.point_token,
            'max_energy_num': self.max_energy_num,
            'max_file_num': self.max_file_num,
            'research_num': self.research_num,
            'build_from_filed_cost_reduction': self.build_from_filed_cost_reduction,
            'build_from_research_cost_reduction': self.build_from_research_cost_reduction,
            'energy_num': self.energy_num,
            'total_energy_num': self.total_energy_num,
            'score': self.score,
        }

    @property
    def can_add_energy(self):
        return self.max_energy_num > self.total_energy_num

    @property
    def avail_gizmos(self):
        return [g for g in self.gizmos if g.active and not g.used]

    @property
    def can_file(self):
        return len(self.filed) < self.max_file_num

    @property
    def can_research(self):
        return self.research_num > 0

    @property
    def score(self):
        total_gizmo_value = sum(g.get_value(self) for g in self.gizmos)
        return total_gizmo_value + self.point_token

    @property
    def total_energy_num(self):
        return calc_total_energy_num(self.energy_num)

    @property
    def upgrade_gizmos(self) -> Set[UpgradeGizmo]:
        return self.gizmos_by_type[GizmoType.UPGRADE]

    @property
    def converter_gizmos(self) -> Set[ConverterGizmo]:
        return self.gizmos_by_type[GizmoType.CONVERTER]

    @property
    def pick_gizmos(self) -> Set[PickGizmo]:
        return self.gizmos_by_type[GizmoType.PICK]

    @property
    def build_gizmos(self) -> Set[BuildGizmo]:
        return self.gizmos_by_type[GizmoType.BUILD]

    @property
    def file_gizmos(self) -> Set[FileGizmo]:
        return self.gizmos_by_type[GizmoType.FILE]

    @property
    def level3_gizmos(self):
        return list(filter(lambda g: g.level == 3, self.gizmos))

    def calc_cost_reduction(self, method: BuildMethod):
        reduction = 0
        if method == BuildMethod.FROM_FILED:
            reduction += self.build_from_filed_cost_reduction
        elif method == BuildMethod.FROM_RESEARCH:
            reduction += self.build_from_research_cost_reduction
        return reduction

    def build_solutions(self, gizmo: Gizmo, method: BuildMethod, cost_energy_num: Dict[Energy, int], cost_converter_gizmos: List[Gizmo], check_only=False):
        if gizmo in self.gizmos:
            print('[build_solutions] already built')
            return []
        if self.env.check and any(not g.is_satisfied(gizmo) or g not in self.gizmos for g in cost_converter_gizmos):
            print('[build_solutions] invalid gizmo used')
            return []
        cost_reduction = self.calc_cost_reduction(method)
        solutions = find_build_solutions(
            gizmo.energy_type, gizmo.energy_cost - cost_reduction, cost_energy_num, cost_converter_gizmos, check_only)
        return sorted(solutions, key=lambda s: calc_total_energy_num(s['energy_num']))
