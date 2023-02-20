from typing import List, Dict, TypedDict
from queue import Queue

from gizmos_utils import init_energy_num
from Gizmo import ConverterGizmo
from common import Energy, EnergyWithAny
from utils import proper_subsets, list_compose

ALL_ENERGY_TYPES = ['red', 'blue', 'black', 'yellow']


class BuildSolution(TypedDict):
    gizmos: List[ConverterGizmo]
    energy_num: Dict[Energy, int]


class TmpBuildSolution(TypedDict):
    energy_cost: int
    avail_energy: Dict[Energy, int]
    avail_gizmos: List[ConverterGizmo]
    extra_energy: Dict[EnergyWithAny, int]
    gizmos: List[ConverterGizmo]
    energy_num: Dict[Energy, int]


def has_better_solution(solution: BuildSolution, solutions: List[BuildSolution]) -> bool:
    return any(
        s for s in solutions
        if all(s['energy_num'][curr] <= solution['energy_num'][curr] for curr in ALL_ENERGY_TYPES)
        and (len(s['gizmos']) <= len(solution['gizmos']) and all(g in solution['gizmos'] for g in s['gizmos']))
    )


def clone_solution(solution) -> BuildSolution:
    return {
        'energy_num': solution['energy_num'].copy(),
        'gizmos': solution['gizmos'].copy(),
    }


def clone_ts(ts: TmpBuildSolution) -> TmpBuildSolution:
    return {
        'energy_cost': ts['energy_cost'],
        'avail_energy': {
            'red': ts['avail_energy']['red'],
            'yellow': ts['avail_energy']['yellow'],
            'blue': ts['avail_energy']['blue'],
            'black': ts['avail_energy']['black'],
        },
        'avail_gizmos': ts['avail_gizmos'].copy(),
        'extra_energy': {
            'red': ts['extra_energy']['red'],
            'yellow': ts['extra_energy']['yellow'],
            'blue': ts['extra_energy']['blue'],
            'black': ts['extra_energy']['black'],
            'any': ts['extra_energy']['any'],
        },
        'gizmos': ts['gizmos'].copy(),
        'energy_num': {
            'red': ts['energy_num']['red'],
            'yellow': ts['energy_num']['yellow'],
            'blue': ts['energy_num']['blue'],
            'black': ts['energy_num']['black'],
        },
    }


def apply_formula(ts: TmpBuildSolution, formula) -> bool:
    # assume `formula['from']['num']` always be 1
    if formula['from']['num'] != 1:
        raise Exception('formula.from.num not 1')

    from_e = formula['from']['energy']
    if ts['extra_energy'][from_e] > 0:
        ts['extra_energy'][from_e] -= 1
    elif ts['avail_energy'][from_e] > 0:
        ts['avail_energy'][from_e] -= 1
        ts['energy_num'][from_e] += 1
    else:
        return False
    ts['extra_energy'][formula['to']['energy']] += formula['to']['num']
    return True


def apply_formula_any(ts: TmpBuildSolution, formula) -> bool:
    # assume `formula['from']['num']` always be 1
    if formula['from']['num'] != 1:
        raise Exception('formula.from.num not 1')

    if ts['extra_energy']['any'] > 0:
        ts['extra_energy']['any'] -= 1
    else:
        return False
    ts['extra_energy'][formula['to']['energy']] += formula['to']['num']
    return True


def apply_gizmo(ts: TmpBuildSolution, gizmo: ConverterGizmo) -> None:
    ts['gizmos'].append(gizmo)
    ts['avail_gizmos'] = [g for g in ts['avail_gizmos'] if g != gizmo]


def not_from_any_formula(formula) -> bool:
    return formula['from']['energy'] != 'any'


def find_build_solutions(
    energy_type: Energy,
    energy_cost: int,
    avail_energy: Dict[Energy, int],
    avail_gizmos: List[ConverterGizmo],
    check_only: bool,
):
    tmp_solutions: Queue[TmpBuildSolution] = Queue()
    tmp_solutions.put({
        'energy_cost': energy_cost,
        'avail_energy': avail_energy.copy(),
        'avail_gizmos': avail_gizmos.copy(),
        'extra_energy': {'red': 0, 'yellow': 0, 'blue': 0, 'black': 0, 'any': 0},
        'gizmos': [],
        'energy_num': init_energy_num(),
    })
    solutions: List[BuildSolution] = []

    def apply_solution(solution: BuildSolution) -> bool:
        nonlocal solutions
        if has_better_solution(solution, solutions):
            return False
        solutions = [s for s in solutions if not has_better_solution(s, [
                                                                     solution])]
        solutions.append(solution)
        return True

    while tmp_solutions.qsize() > 0:
        if check_only and len(solutions) > 0:
            break
        ts = tmp_solutions.get()
        if not ts:
            raise Exception('no ts')

        # collect solutions if possible
        if energy_type == 'any':
            avail = ts['avail_energy']
            total_avail = avail['red'] + avail['yellow'] + \
                avail['blue'] + avail['black']
            total_extra_energy = (
                ts['extra_energy']['red'] +
                ts['extra_energy']['yellow'] +
                ts['extra_energy']['blue'] +
                ts['extra_energy']['black'] +
                ts['extra_energy']['any']
            )
            raw_cost = energy_cost - total_extra_energy

            if total_avail >= raw_cost:
                if raw_cost <= 0:
                    apply_solution(clone_solution(ts))
                    continue

                max_red = min(avail['red'], raw_cost)
                min_red = max(0, raw_cost - avail['yellow'] -
                              avail['blue'] - avail['black'])
                for red in range(min_red, max_red + 1):
                    raw_cost1 = raw_cost - red
                    if raw_cost1 < 0:
                        break
                    max_yellow = min(avail['yellow'], raw_cost1)
                    min_yellow = max(
                        0, raw_cost1 - avail['blue'] - avail['black'])
                    for yellow in range(min_yellow, max_yellow + 1):
                        raw_cost2 = raw_cost1 - yellow
                        if raw_cost2 < 0:
                            break
                        max_blue = min(avail['blue'], raw_cost2)
                        min_blue = max(0, raw_cost2 - avail['black'])
                        for blue in range(min_blue, max_blue + 1):
                            raw_cost3 = raw_cost2 - blue
                            if raw_cost3 < 0:
                                break
                            black = raw_cost3
                            solution = clone_solution(ts)
                            solution['energy_num']['red'] += red
                            solution['energy_num']['yellow'] += yellow
                            solution['energy_num']['blue'] += blue
                            solution['energy_num']['black'] += black
                            apply_solution(solution)
        else:
            raw_cost = energy_cost - \
                ts['extra_energy'][energy_type] - ts['extra_energy']['any']
            if ts['avail_energy'][energy_type] >= raw_cost:
                solution = clone_solution(ts)
                if raw_cost > 0:
                    solution['energy_num'][energy_type] += raw_cost
                if not apply_solution(solution):
                    continue

        # try to use a gizmo
        for gizmo in ts['avail_gizmos']:
            base_new_ts = clone_ts(ts)
            apply_gizmo(base_new_ts, gizmo)

            # try all possible formula combinations of the gizmo
            for formulae in proper_subsets(gizmo.formulae):
                opt_groups: List[List] = []
                for formula in formulae:
                    options: List = []
                    if not_from_any_formula(formula):
                        options.append((formula, apply_formula))
                        if formula['to']['num'] > 1:
                            options.append((formula, apply_formula_any))
                    else:
                        for energy in ALL_ENERGY_TYPES:
                            detailed_formula = {
                                'from': {
                                    'energy': energy,
                                    'num': formula['from']['num'],
                                },
                                'to': formula['to'],
                            }
                            options.append((detailed_formula, apply_formula))
                    opt_groups.append(options)
                if len(opt_groups) <= 0:
                    continue
                for strategy in list_compose(opt_groups):
                    new_ts = clone_ts(base_new_ts)
                    if any(fn(new_ts, formula) for [formula, fn] in strategy):
                        tmp_solutions.put(new_ts)

    return solutions
