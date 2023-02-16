import {
  type Energy,
  type AllGizmoLevel,
  ALL_ENERGY_TYPES,
  BuildMethod,
} from './common'
import { find_build_solutions } from './find_build_solutions'
import {
  ConverterGizmo,
  Gizmo,
  is_upgrade_gizmo,
  is_converter_gizmo,
  is_pick_gizmo,
  is_build_gizmo,
  is_file_gizmo,
  GizmoInfo,
  GizmoType,
  UpgradeGizmo,
  PickGizmo,
  BuildGizmo,
  FileGizmo,
} from './Gizmo'
import type { GizmosEnv } from './GizmosEnv'
import { init_energy_num } from './gizmos_utils'

export type BuildSolution = {
  gizmos: ConverterGizmo[]
  energy_num: Record<Energy, number>
}
const BASE_MAX_ENERGY = 5
const BASE_MAX_FILE = 1
const BASE_RESEARCH_NUM = 3

function calc_total_energy_num(energy_num: Record<Energy, number>) {
  return Object.values(energy_num).reduce((acc, curr) => acc + curr, 0)
}

export type PlayerInfo = {
  index: number
  gizmos: GizmoInfo<AllGizmoLevel>[]
  upgrade_gizmos: GizmoInfo[]
  converter_gizmos: GizmoInfo[]
  pick_gizmos: GizmoInfo[]
  build_gizmos: GizmoInfo[]
  file_gizmos: GizmoInfo<AllGizmoLevel>[]
  level3_gizmos: GizmoInfo[]
  filed: GizmoInfo[]
  point_token: number
  max_energy_num: number
  max_file_num: number
  research_num: number
  build_from_filed_cost_reduction: number
  build_from_research_cost_reduction: number
  energy_num: Record<Energy, number>
  total_energy_num: number
  score: number
}

export class Player {
  env: GizmosEnv
  index: number

  gizmos: Set<Gizmo<AllGizmoLevel>>
  point_token: number

  energy_num: Record<Energy, number>
  filed: Set<Gizmo>

  gizmos_by_type: {
    [GizmoType.PICK]: Set<PickGizmo>
    [GizmoType.BUILD]: Set<BuildGizmo>
    [GizmoType.UPGRADE]: Set<UpgradeGizmo>
    [GizmoType.CONVERTER]: Set<ConverterGizmo>
    [GizmoType.FILE]: Set<FileGizmo>
  }
  get upgrade_gizmos() {
    return this.gizmos_by_type[GizmoType.UPGRADE] as Set<UpgradeGizmo>
  }
  get converter_gizmos() {
    return this.gizmos_by_type[GizmoType.CONVERTER] as Set<ConverterGizmo>
  }
  get pick_gizmos() {
    return this.gizmos_by_type[GizmoType.PICK] as Set<PickGizmo>
  }
  get build_gizmos() {
    return this.gizmos_by_type[GizmoType.BUILD] as Set<BuildGizmo>
  }
  get file_gizmos() {
    return this.gizmos_by_type[GizmoType.FILE] as Set<FileGizmo>
  }

  get level3_gizmos() {
    return [...this.gizmos].filter(g => g.level === 3) as Gizmo[]
  }

  max_energy_num: number
  max_file_num: number
  research_num: number
  build_from_filed_cost_reduction: number
  build_from_research_cost_reduction: number

  get total_energy_num() {
    return calc_total_energy_num(this.energy_num)
  }

  get can_add_energy() {
    return this.max_energy_num > this.total_energy_num
  }

  get avail_gizmos() {
    return [...this.gizmos].filter(g => g.active && !g.used)
  }

  get can_file() {
    return this.filed.size < this.max_file_num
  }

  get can_research() {
    return this.research_num > 0
  }

  get score() {
    const total_gizmo_value = [...this.gizmos].reduce(
      (acc, curr) => acc + curr.get_value(this),
      0
    )
    return total_gizmo_value + this.point_token
  }

  calc_cost_reduction(method: BuildMethod) {
    let reduction = 0
    if (method === BuildMethod.FROM_FILED) {
      reduction += this.build_from_filed_cost_reduction
    } else if (method === BuildMethod.FROM_RESEARCH) {
      reduction += this.build_from_research_cost_reduction
    }
    return reduction
  }

  build_solutions(
    gizmo: Gizmo,
    method: BuildMethod,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos: ConverterGizmo[],
    check_only = false
  ): BuildSolution[] {
    if (this.gizmos.has(gizmo)) {
      console.error('[build_solutions] already built')
      return []
    }
    if (
      this.env.check &&
      cost_converter_gizmos.some(
        g => !g.is_satisfied(gizmo) || !this.gizmos.has(g)
      )
    ) {
      console.error('[build_solutions] invalid gizmo used')
      return []
    }
    const cost_reduction = this.calc_cost_reduction(method)
    const solutions = find_build_solutions(
      gizmo.energy_type,
      gizmo.energy_cost - cost_reduction,
      cost_energy_num,
      cost_converter_gizmos,
      check_only
    )
    return solutions.sort(
      (a, b) =>
        calc_total_energy_num(a.energy_num) -
        calc_total_energy_num(b.energy_num)
    )
  }

  add_energy = (energy: Energy) => {
    if (!this.can_add_energy) return
    this.energy_num[energy] += 1
  }

  add_gizmo = (gizmo: Gizmo<AllGizmoLevel>) => {
    this.gizmos.add(gizmo)
    if (is_pick_gizmo(gizmo)) {
      this.gizmos_by_type[GizmoType.PICK].add(gizmo)
    } else if (is_build_gizmo(gizmo)) {
      this.gizmos_by_type[GizmoType.BUILD].add(gizmo)
    } else if (is_upgrade_gizmo(gizmo)) {
      this.gizmos_by_type[GizmoType.UPGRADE].add(gizmo)
      this.max_energy_num += gizmo.max_energy_num
      this.max_file_num += gizmo.max_file_num
      this.research_num += gizmo.research_num
      this.build_from_filed_cost_reduction +=
        gizmo.build_from_filed_cost_reduction
      this.build_from_research_cost_reduction +=
        gizmo.build_from_research_cost_reduction
    } else if (is_converter_gizmo(gizmo)) {
      this.gizmos_by_type[GizmoType.CONVERTER].add(gizmo)
    } else if (is_file_gizmo(gizmo)) {
      this.gizmos_by_type[GizmoType.FILE].add(gizmo)
    }
  }

  pick_from_file(id: number) {
    const gizmo = this.env.gizmo(id)
    if (!this.filed.has(gizmo)) {
      throw new Error("[pick_from_file] not in player's file")
    }
    this.filed.delete(gizmo)
    return gizmo
  }

  pick(energy: Energy) {
    this.add_energy(energy)
    this.pick_gizmos.forEach(g => g.on_pick(energy))
  }

  file(gizmo: Gizmo) {
    if (!this.can_file) {
      throw new Error('file overflow')
    }
    this.filed.add(gizmo)
    this.file_gizmos.forEach(g => g.on_file())
  }

  build(
    gizmo: Gizmo,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[],
    method = BuildMethod.DIRECTLY
  ) {
    const converter_gizmos = [...this.converter_gizmos].filter(gizmo =>
      cost_converter_gizmos_id.includes(gizmo.id)
    )
    if (converter_gizmos.length !== cost_converter_gizmos_id.length) {
      throw new Error('unexpected gizmo(s) used')
    }

    if (
      this.env.check &&
      this.build_solutions(
        gizmo,
        method,
        cost_energy_num,
        converter_gizmos,
        true
      ).length <= 0
    ) {
      throw new Error('no build solution')
    }
    converter_gizmos.forEach(g => g.on_convert(gizmo))
    converter_gizmos.forEach(g => g.used_by(this))
    this.drop(cost_energy_num)
    this.build_gizmos.forEach(g =>
      g.on_build(this, gizmo.level, gizmo.energy_type, method)
    )
    this.add_gizmo(gizmo)
  }

  build_from_filed(
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) {
    const gizmo = this.pick_from_file(id)
    this.build(
      gizmo,
      cost_energy_num,
      cost_converter_gizmos_id,
      BuildMethod.FROM_FILED
    )
  }

  build_from_research(
    gizmo: Gizmo,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) {
    this.build(
      gizmo,
      cost_energy_num,
      cost_converter_gizmos_id,
      BuildMethod.FROM_RESEARCH
    )
  }

  build_for_free(gizmo: Gizmo) {
    this.build_gizmos.forEach(g =>
      g.on_build(this, gizmo.level, gizmo.energy_type, BuildMethod.DIRECTLY)
    )
    this.add_gizmo(gizmo)
  }

  drop(energy_num: Record<Energy, number>) {
    ALL_ENERGY_TYPES.forEach(energy => {
      if (this.energy_num[energy] < energy_num[energy]) {
        throw new Error('not enough energy to drop')
      }
      this.energy_num[energy] -= energy_num[energy]
    })
    this.env.drop_energy_to_pool(energy_num)
    if (this.total_energy_num > this.max_energy_num) {
      throw new Error('energy overflow after drop')
    }
  }

  use_gizmo(id: number) {
    const gizmo = this.env.u_gizmo(id)
    if (!this.gizmos.has(gizmo)) {
      throw new Error("[use_gizmo] not in player's gizmos")
    }
    this.env.state.gizmos[id].used_by(this)
  }

  reset_gizmos() {
    this.gizmos.forEach(g => g.reset())
  }

  get info(): PlayerInfo {
    return {
      index: this.index,
      gizmos: [...this.gizmos].map(g => g.info),
      upgrade_gizmos: [...this.upgrade_gizmos].map(g => g.info),
      converter_gizmos: [...this.converter_gizmos].map(g => g.info),
      pick_gizmos: [...this.pick_gizmos].map(g => g.info),
      build_gizmos: [...this.build_gizmos].map(g => g.info),
      file_gizmos: [...this.file_gizmos].map(g => g.info),
      level3_gizmos: this.level3_gizmos.map(g => g.info),
      filed: [...this.filed].map(g => g.info),
      point_token: this.point_token,
      max_energy_num: this.max_energy_num,
      max_file_num: this.max_file_num,
      research_num: this.research_num,
      build_from_filed_cost_reduction: this.build_from_filed_cost_reduction,
      build_from_research_cost_reduction:
        this.build_from_research_cost_reduction,
      energy_num: this.energy_num,
      total_energy_num: this.total_energy_num,
      score: this.score,
    }
  }

  constructor({
    env,
    index,
    gizmos,
    point_token,
    energy_num,
    filed,
  }: {
    env: GizmosEnv
    index: number
    gizmos?: Gizmo<AllGizmoLevel>[]
    point_token?: number
    energy_num?: Record<Energy, number>
    filed?: Gizmo[]
  }) {
    this.env = env
    this.index = index
    this.max_energy_num = BASE_MAX_ENERGY
    this.max_file_num = BASE_MAX_FILE
    this.research_num = BASE_RESEARCH_NUM
    this.build_from_filed_cost_reduction = 0
    this.build_from_research_cost_reduction = 0
    this.gizmos = new Set()
    this.gizmos_by_type = {
      [GizmoType.PICK]: new Set(),
      [GizmoType.BUILD]: new Set(),
      [GizmoType.UPGRADE]: new Set(),
      [GizmoType.CONVERTER]: new Set(),
      [GizmoType.FILE]: new Set(),
    }
    ;(gizmos ?? []).forEach(this.add_gizmo)
    this.point_token = point_token ?? 0
    this.energy_num = energy_num ?? init_energy_num()
    this.filed = new Set(filed)
  }
}
