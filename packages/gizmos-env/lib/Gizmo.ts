import {
  type GizmoLevel,
  type EnergyWithAny,
  type Energy,
  type AllGizmoLevel,
  BuildMethod,
  Stage,
} from './common'
import type { Player } from './Player'

export enum GizmoType {
  PICK = 'PICK',
  BUILD = 'BUILD',
  UPGRADE = 'UPGRADE',
  CONVERTER = 'CONVERTER',
  FILE = 'FILE',
}
export type Effect =
  | { type: 'na' }
  | { type: 'free_draw'; num: number }
  | { type: 'free_pick'; num: number }
  | { type: 'add_point_token'; num: number }
  | { type: 'extra_file' }
  | { type: 'extra_research' }
  | { type: 'extra_build'; level: GizmoLevel[] }
  | { type: 'energy_as_point' }
  | { type: 'token_as_point' }
export interface GizmoBasic<Level = GizmoLevel> {
  id: number
  level: Level
  energy_type: EnergyWithAny
  energy_cost: number
  value: number
  effect?: Effect
}
export interface GizmoInfo {
  id: number
  active: boolean
  used: boolean
  where: 'unknown' | 'board' | 'research' | 'file' | 'player'
  belongs_to: number | null
}
export abstract class Gizmo<Level = GizmoLevel> {
  abstract type: GizmoType
  id: number
  level: Level
  energy_type: EnergyWithAny
  energy_cost: number
  value: number
  effect: Effect

  active: boolean
  used: boolean

  where: 'excluded' | 'pool' | 'board' | 'research' | 'file' | 'player'
  belongs_to: number | null

  assert_available() {
    if (!this.active) {
      throw new Error('gizmo not activated')
    }
    if (this.used) {
      throw new Error('gizmo used')
    }
  }

  used_by(player: Player) {
    this.assert_available()
    switch (this.effect.type) {
      case 'free_draw':
        this.free_draw(player, this.effect.num)
        break
      case 'free_pick':
        this.free_pick(player, this.effect.num)
        break
      case 'add_point_token':
        this.add_point_token(player, this.effect.num)
        break
      case 'extra_file':
        this.extra_file(player)
        break
      case 'extra_research':
        this.extra_research(player)
        break
      case 'extra_build':
        this.extra_build(player, this.effect.level)
        break
      default:
    }
    this.active = false
    this.used = true
  }

  free_draw(player: Player, num: number) {
    if (player.env.energy_pool_len() <= 0) return
    const draw_num = Math.min(
      num,
      player.max_energy_num - player.total_energy_num
    )
    player.env.draw_energy_from_pool(draw_num).forEach(player.add_energy)
  }

  free_pick(player: Player, num: number) {
    if (player.env.state.energy_board.length <= 0) return
    player.env.state.free_pick_num = num
  }

  add_point_token(player: Player, num: number) {
    player.point_token += num
  }

  extra_file(player: Player) {
    player.env.state.curr_stage === Stage.EXTRA_FILE
  }

  extra_research(player: Player) {
    if (player.research_num <= 0) return
    player.env.state.curr_stage = Stage.EXTRA_RESEARCH
  }

  extra_build(player: Player, level: GizmoLevel[]) {
    player.env.state.free_build = { level }
    player.env.state.curr_stage = Stage.EXTRA_BUILD
  }

  reset_used() {
    this.active = false
    this.used = false
  }

  reset() {
    this.reset_used()
    this.where = 'excluded'
    this.belongs_to = null
  }

  get_value(player: Player) {
    switch (this.effect.type) {
      case 'token_as_point':
        return player.point_token
      case 'energy_as_point':
        return player.total_energy_num
      default:
        return this.value
    }
  }

  get info(): GizmoInfo {
    return {
      id: this.id,
      active: this.active,
      used: this.used,
      where:
        this.where === 'excluded' || this.where === 'pool'
          ? 'unknown'
          : this.where,
      belongs_to: this.belongs_to,
    }
  }

  constructor({
    id,
    level,
    energy_type,
    energy_cost,
    value,
    effect,
  }: GizmoBasic<Level>) {
    this.id = id
    this.level = level
    this.energy_type = energy_type
    this.energy_cost = energy_cost
    this.value = value
    this.effect = effect ?? { type: 'na' }

    this.active = false
    this.used = false

    this.where = 'excluded'
    this.belongs_to = null
  }
}

type GizmoPick = {
  when_pick: Energy[]
}
export class PickGizmo extends Gizmo {
  type = GizmoType.PICK
  when_pick: Energy[]

  is_satisfied(energy: Energy) {
    return this.when_pick.includes(energy)
  }

  on_pick(energy: Energy) {
    if (!this.is_satisfied(energy)) {
      return
    }
    if (!this.used) {
      this.active = true
    }
  }

  constructor({ when_pick, ...basic }: GizmoBasic & GizmoPick) {
    super(basic)
    this.when_pick = when_pick
  }
}

type GizmoBuild = {
  when_build: {
    energy: Energy[] | 'any'
    level: AllGizmoLevel[] | 'any'
    method: BuildMethod[] | 'any'
  }
}
export class BuildGizmo extends Gizmo {
  type = GizmoType.BUILD
  when_build: {
    energy: Energy[] | 'any'
    level: AllGizmoLevel[] | 'any'
    method: BuildMethod[] | 'any'
  }

  is_satisfied(
    player: Player,
    level: GizmoLevel,
    energy: EnergyWithAny,
    method: BuildMethod
  ) {
    return (
      (this.when_build.level === 'any' ||
        this.when_build.level.includes(level)) &&
      (this.when_build.energy === 'any' ||
        energy === 'any' ||
        this.when_build.energy.includes(energy)) &&
      (this.when_build.method === 'any' ||
        this.when_build.method.includes(method)) &&
      (this.effect.type !== 'extra_file' || player.can_file) &&
      (this.effect.type !== 'extra_research' || player.can_research)
    )
  }

  on_build(
    player: Player,
    level: GizmoLevel,
    energy: EnergyWithAny,
    method: BuildMethod
  ) {
    if (!this.is_satisfied(player, level, energy, method)) {
      return
    }
    if (!this.used) {
      this.active = true
    }
  }

  constructor({ when_build, ...basic }: GizmoBasic & GizmoBuild) {
    super(basic)
    this.when_build = when_build
  }
}

type GizmoUpgrade = {
  max_energy_num?: number
  max_file_num?: number
  research_num?: number
  build_from_filed_cost_reduction?: number
  build_from_research_cost_reduction?: number
}
export class UpgradeGizmo extends Gizmo {
  type = GizmoType.UPGRADE
  max_energy_num: number
  max_file_num: number
  research_num: number
  build_from_filed_cost_reduction: number
  build_from_research_cost_reduction: number

  constructor({
    max_energy_num,
    max_file_num,
    research_num,
    build_from_filed_cost_reduction,
    build_from_research_cost_reduction,
    ...basic
  }: GizmoBasic & GizmoUpgrade) {
    super(basic)
    this.max_energy_num = max_energy_num ?? 0
    this.max_file_num = max_file_num ?? 0
    this.research_num = research_num ?? 0
    this.build_from_filed_cost_reduction = build_from_filed_cost_reduction ?? 0
    this.build_from_research_cost_reduction =
      build_from_research_cost_reduction ?? 0
  }
}

export type ConverterFormula<EF = EnergyWithAny, ET = EnergyWithAny> = {
  from: {
    energy: EF
    num: number
  }
  to: {
    energy: ET
    num: number
  }
}
type GizmoConverter = {
  prerequisite?: {
    level: AllGizmoLevel[]
  }
  formulae: ConverterFormula[]
}
export class ConverterGizmo extends Gizmo {
  type = GizmoType.CONVERTER
  prerequisite?: { level: AllGizmoLevel[] }
  formulae: ConverterFormula[]

  is_satisfied(gizmo: Gizmo) {
    return (
      !this.used &&
      (!this.prerequisite || this.prerequisite.level.includes(gizmo.level))
    )
  }

  on_convert(gizmo: Gizmo) {
    if (!this.is_satisfied(gizmo)) return
    this.active = true
  }

  constructor({
    prerequisite,
    formulae,
    ...basic
  }: GizmoBasic & GizmoConverter) {
    super(basic)
    this.prerequisite = prerequisite
    this.formulae = formulae
  }
}

// eslint-disable-next-line @typescript-eslint/ban-types
type GizmoFile = {}
export class FileGizmo<Level = GizmoLevel> extends Gizmo<Level> {
  type = GizmoType.FILE

  on_file() {
    if (!this.used) {
      this.active = true
    }
  }
  constructor({ ...basic }: GizmoBasic<Level> & GizmoFile) {
    super(basic)
  }
}

export function is_upgrade_gizmo(
  gizmo: Gizmo<AllGizmoLevel>
): gizmo is UpgradeGizmo {
  return gizmo instanceof UpgradeGizmo
}
export function is_converter_gizmo(
  gizmo: Gizmo<AllGizmoLevel>
): gizmo is ConverterGizmo {
  return gizmo instanceof ConverterGizmo
}
export function is_pick_gizmo(gizmo: Gizmo<AllGizmoLevel>): gizmo is PickGizmo {
  return gizmo instanceof PickGizmo
}
export function is_build_gizmo(
  gizmo: Gizmo<AllGizmoLevel>
): gizmo is BuildGizmo {
  return gizmo instanceof BuildGizmo
}
export function is_file_gizmo(gizmo: Gizmo<AllGizmoLevel>): gizmo is FileGizmo {
  return gizmo instanceof FileGizmo
}
