import { type EnergyWithAny, type Energy, ALL_ENERGY_TYPES } from './common'
import type { ConverterFormula, ConverterGizmo } from './Gizmo'
import { init_energy_num } from './gizmos_utils'
import type { BuildSolution } from './Player'
import { list_compose, proper_subsets } from './utils'

type TmpBuildSolution = {
  energy_cost: number
  avail_energy: Record<Energy, number>
  avail_gizmos: ConverterGizmo[]
  extra_energy: Record<EnergyWithAny, number>
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

function clone_solution(solution: BuildSolution | TmpBuildSolution) {
  return {
    energy_num: { ...solution.energy_num },
    gizmos: [...solution.gizmos],
  }
}

function clone_ts(ts: TmpBuildSolution): TmpBuildSolution {
  return {
    energy_cost: ts.energy_cost,
    avail_energy: {
      red: ts.avail_energy.red,
      yellow: ts.avail_energy.yellow,
      blue: ts.avail_energy.blue,
      black: ts.avail_energy.black,
    },
    avail_gizmos: [...ts.avail_gizmos],
    extra_energy: {
      red: ts.extra_energy.red,
      yellow: ts.extra_energy.yellow,
      blue: ts.extra_energy.blue,
      black: ts.extra_energy.black,
      any: ts.extra_energy.any,
    },
    gizmos: [...ts.gizmos],
    energy_num: {
      red: ts.energy_num.red,
      yellow: ts.energy_num.yellow,
      blue: ts.energy_num.blue,
      black: ts.energy_num.black,
    },
  }
}

function apply_formula(
  ts: TmpBuildSolution,
  formula: ConverterFormula<Energy>
) {
  // assume `formula.from.num` always be 1
  if (formula.from.num !== 1) {
    throw new Error('formula.from.num not 1')
  }

  const from_e = formula.from.energy
  if (ts.extra_energy[from_e] > 0) {
    ts.extra_energy[from_e] -= 1
  } else if (ts.avail_energy[from_e] > 0) {
    ts.avail_energy[from_e] -= 1
    ts.energy_num[from_e] += 1
  } else {
    return false
  }
  ts.extra_energy[formula.to.energy] += formula.to.num
  return true
}

function apply_formula_any(
  ts: TmpBuildSolution,
  formula: ConverterFormula<Energy>
) {
  // assume `formula.from.num` always be 1
  if (formula.from.num !== 1) {
    throw new Error('formula.from.num not 1')
  }

  if (ts.extra_energy.any > 0) {
    ts.extra_energy.any -= 1
  } else {
    return false
  }
  ts.extra_energy[formula.to.energy] += formula.to.num
  return true
}

type ApplyFormulaOption = [
  ConverterFormula<Energy>,
  typeof apply_formula | typeof apply_formula_any
]

function apply_gizmo(ts: TmpBuildSolution, gizmo: ConverterGizmo) {
  ts.gizmos.push(gizmo)
  ts.avail_gizmos = ts.avail_gizmos.filter(g => g != gizmo)
}

function not_from_any_formula(
  formula: ConverterFormula
): formula is ConverterFormula<Energy> {
  return formula.from.energy !== 'any'
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
      extra_energy: { red: 0, yellow: 0, blue: 0, black: 0, any: 0 },
      gizmos: [],
      energy_num: init_energy_num(),
    },
  ])
  let solutions: BuildSolution[] = []
  function apply_solution(solution: BuildSolution) {
    if (has_better_solution(solution, solutions)) {
      return false
    }
    solutions = solutions.filter(s => !has_better_solution(s, [solution]))
    solutions.push(solution)
    return true
  }

  while (tmp_solutions.length > 0) {
    if (check_only && solutions.length > 0) {
      break
    }
    const ts = tmp_solutions.shift()
    if (!ts) {
      throw new Error('no ts')
    }

    // collect solutions if possible
    if (energy_type === 'any') {
      const avail = ts.avail_energy
      const total_avail = avail.red + avail.yellow + avail.blue + avail.black
      const total_extra_energy =
        ts.extra_energy.red +
        ts.extra_energy.yellow +
        ts.extra_energy.blue +
        ts.extra_energy.black +
        ts.extra_energy.any
      const raw_cost = energy_cost - total_extra_energy

      if (total_avail >= raw_cost) {
        if (raw_cost <= 0) {
          apply_solution(clone_solution(ts))
          continue
        }

        const max_red = Math.min(avail.red, raw_cost)
        const min_red = Math.max(
          0,
          raw_cost - avail.yellow - avail.blue - avail.black
        )
        for (let red = min_red; red <= max_red; red++) {
          const raw_cost1 = raw_cost - red
          if (raw_cost1 < 0) break
          const max_yellow = Math.min(avail.yellow, raw_cost1)
          const min_yellow = Math.max(0, raw_cost1 - avail.blue - avail.black)
          for (let yellow = min_yellow; yellow <= max_yellow; yellow++) {
            const raw_cost2 = raw_cost1 - yellow
            if (raw_cost2 < 0) break
            const max_blue = Math.min(avail.blue, raw_cost2)
            const min_blue = Math.max(0, raw_cost2 - avail.black)
            for (let blue = min_blue; blue <= max_blue; blue++) {
              const raw_cost3 = raw_cost2 - blue
              if (raw_cost3 < 0) break
              const black = raw_cost3
              const solution = clone_solution(ts)
              solution.energy_num.red += red
              solution.energy_num.yellow += yellow
              solution.energy_num.blue += blue
              solution.energy_num.black += black
              apply_solution(solution)
            }
          }
        }
      }
    } else {
      const raw_cost =
        energy_cost - ts.extra_energy[energy_type] - ts.extra_energy.any
      if (ts.avail_energy[energy_type] >= raw_cost) {
        const solution = clone_solution(ts)
        if (raw_cost > 0) {
          solution.energy_num[energy_type] += raw_cost
        }
        if (!apply_solution(solution)) {
          continue
        }
      }
    }

    // try to use a gizmo
    ts.avail_gizmos.forEach(gizmo => {
      const base_new_ts = clone_ts(ts)
      apply_gizmo(base_new_ts, gizmo)

      // try all possible formula combinations of the gizmo
      proper_subsets(gizmo.formulae).forEach(formulae => {
        const opt_groups: ApplyFormulaOption[][] = []
        formulae.forEach(formula => {
          const options: ApplyFormulaOption[] = []
          if (not_from_any_formula(formula)) {
            options.push([formula, apply_formula])
            if (formula.to.num > 1) {
              options.push([formula, apply_formula_any])
            }
          } else {
            ALL_ENERGY_TYPES.forEach(energy => {
              const detailed_formula = {
                from: {
                  energy,
                  num: formula.from.num,
                },
                to: formula.to,
              }
              options.push([detailed_formula, apply_formula])
            })
          }
          opt_groups.push(options)
        })
        list_compose(opt_groups).forEach(strategy => {
          const new_ts = clone_ts(base_new_ts)
          if (
            strategy.map(([formula, fn]) => fn(new_ts, formula)).some(v => v)
          ) {
            tmp_solutions.push(new_ts)
          }
        })
      })
    })
  }

  return solutions
}
