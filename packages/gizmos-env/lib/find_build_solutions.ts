import { type EnergyWithAny, type Energy, ALL_ENERGY_TYPES } from './common'
import type { ConverterFormula, ConverterGizmo } from './Gizmo'
import { init_energy_num } from './gizmos_utils'
import type { BuildSolution } from './Player'
import { list_compose, proper_subsets } from './utils'

type TmpBuildSolution = {
  energy_cost: number
  avail_energy: Record<Energy, number>
  avail_gizmos: ConverterGizmo[]
  extra_energy: Record<Energy, number>
  gizmos: ConverterGizmo[]
  energy_num: Record<Energy, number>
}
function has_better_solution(
  solution: BuildSolution,
  solutions: BuildSolution[]
) {
  return solutions.some(s => {
    const less_energy_used = ALL_ENERGY_TYPES.reduce(
      (acc, curr) => acc && s.energy_num[curr] <= solution.energy_num[curr],
      true
    )
    const less_gizmos_used =
      s.gizmos.length <= solution.gizmos.length &&
      s.gizmos.every(g => solution.gizmos.includes(g))
    return less_energy_used && less_gizmos_used
  })
}

function detailed_energy(energy: EnergyWithAny) {
  return energy === 'any' ? [...ALL_ENERGY_TYPES] : [energy]
}

function clone_solution(solution: BuildSolution) {
  return {
    energy_num: { ...solution.energy_num },
    gizmos: [...solution.gizmos],
  }
}

function clone_ts(ts: TmpBuildSolution) {
  return {
    energy_cost: ts.energy_cost,
    avail_energy: { ...ts.avail_energy },
    avail_gizmos: [...ts.avail_gizmos],
    extra_energy: { ...ts.extra_energy },
    gizmos: ts.gizmos.concat(),
    energy_num: { ...ts.energy_num },
  }
}

function apply_formula(
  ts: TmpBuildSolution,
  formula: ConverterFormula<Energy>
) {
  const from_e = formula.from.energy
  const from_n = formula.from.num
  if (ts.extra_energy[from_e] >= from_n) {
    ts.extra_energy[from_e] -= from_n
  } else if (ts.extra_energy[from_e] + ts.avail_energy[from_e] >= from_n) {
    const avail_energy_cost = from_n - ts.extra_energy[from_e]
    ts.extra_energy[from_e] = 0
    ts.avail_energy[from_e] -= avail_energy_cost
    ts.energy_num[from_e] += avail_energy_cost
  } else {
    return
  }
  ts.extra_energy[formula.to.energy] += formula.to.num
}

function apply_gizmo(ts: TmpBuildSolution, gizmo: ConverterGizmo) {
  ts.gizmos.push(gizmo)
  ts.avail_gizmos = ts.avail_gizmos.filter(g => g != gizmo)
}

class Q<T> {
  #stack1: T[] = []
  #stack2: T[] = []

  push(item: T) {
    this.#stack1.push(item)
  }

  shift() {
    if (this.#stack2.length === 0) {
      const tmp = this.#stack2
      this.#stack2 = this.#stack1.reverse()
      this.#stack1 = tmp
    }
    return this.#stack2.pop()
  }

  get length() {
    return this.#stack1.length + this.#stack2.length
  }

  constructor(arr?: T[]) {
    if (arr) this.#stack1 = arr.concat()
  }
}

export function find_build_solutions(
  energy_type: EnergyWithAny,
  energy_cost: number,
  avail_energy: Record<Energy, number>,
  avail_gizmos: ConverterGizmo[],
  check_only: boolean
) {
  const tmp_solutions = new Q<TmpBuildSolution>([
    {
      energy_cost,
      avail_energy: { ...avail_energy },
      avail_gizmos: [...avail_gizmos],
      extra_energy: init_energy_num(),
      gizmos: [],
      energy_num: init_energy_num(),
    },
  ])
  let solutions: BuildSolution[] = []

  const ENERGY_TYPES =
    energy_type === 'any' ? [...ALL_ENERGY_TYPES] : [energy_type]

  while (tmp_solutions.length > 0) {
    if (check_only && solutions.length > 0) {
      break
    }
    const ts = tmp_solutions.shift()
    if (!ts) {
      throw new Error('no ts')
    }
    if (has_better_solution(ts, solutions)) {
      continue
    }

    // solved
    if (ts.energy_cost <= 0) {
      const solution = clone_solution(ts)
      Object.entries(solution.energy_num).forEach(([energy, num]) => {
        if (num < 0) solution.energy_num[energy as Energy] = 0
      })
      solutions = solutions.filter(s => !has_better_solution(s, [solution]))
      solutions.push(solution)
      continue
    }

    // try to use an energy
    ENERGY_TYPES.forEach(energy => {
      const new_ts = clone_ts(ts)
      new_ts.energy_cost -= 1
      if (ts.extra_energy[energy] > 0) {
        new_ts.extra_energy[energy] -= 1
        tmp_solutions.push(new_ts)
      } else if (ts.avail_energy[energy] > 0) {
        new_ts.avail_energy[energy] -= 1
        new_ts.energy_num[energy] += 1
        tmp_solutions.push(new_ts)
      }
    })

    // try to use a gizmo
    ts.avail_gizmos.forEach(gizmo => {
      const base_new_ts = clone_ts(ts)
      apply_gizmo(base_new_ts, gizmo)

      // try all possible formula combinations of the gizmo
      proper_subsets(gizmo.formulae).forEach(formulae => {
        const formulae_list: ConverterFormula<Energy>[][] = []
        formulae.forEach(formula => {
          // consider 'any' case
          const energy_from_list = detailed_energy(formula.from.energy)
          const energy_to_list = detailed_energy(formula.to.energy)

          const detailed_formula_group: ConverterFormula<Energy>[] = []
          energy_from_list.forEach(energy_from => {
            energy_to_list.forEach(energy_to => {
              detailed_formula_group.push({
                from: {
                  energy: energy_from,
                  num: formula.from.num,
                },
                to: {
                  energy: energy_to,
                  num: formula.to.num,
                },
              })
            })
          })
          formulae_list.push(detailed_formula_group)
        })
        const formula_groups = list_compose(formulae_list)
        formula_groups.forEach(formula_group => {
          const new_ts = clone_ts(base_new_ts)
          formula_group.forEach(formula => {
            apply_formula(new_ts, formula)
          })
          tmp_solutions.push(new_ts)
        })
      })
    })
  }

  return solutions
}
