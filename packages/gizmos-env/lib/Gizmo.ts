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
  | { type: 'draw_from_pool'; num: number }
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
export interface GizmoInfo<Level = GizmoLevel> {
  type: GizmoType
  id: number
  level: Level
  energy_type: EnergyWithAny
  energy_cost: number
  value: number
  effect: Effect
  active: boolean
  used: boolean
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
      case 'draw_from_pool':
        this.draw_from_pool(player, this.effect.num)
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

  draw_from_pool(player: Player, num: number) {
    if (player.env.energy_pool_len() <= 0) {
      return
    }
    player.env.pick_energy_from_pool(num).forEach(player.add_energy)
  }

  free_pick(player: Player, num: number) {
    if (player.env.state.energy_board.length <= 0) {
      return
    }
    player.env.state.free_pick_num = num
  }

  add_point_token(player: Player, num: number) {
    player.point_token += num
  }

  extra_file(player: Player) {
    player.env.state.curr_stage === Stage.CHOOSE_FILE
  }

  extra_research(player: Player) {
    player.env.state.curr_stage = Stage.CHOOSE_RESEARCH
  }

  extra_build(player: Player, level: GizmoLevel[]) {
    player.env.state.free_build = { level }
    player.env.state.curr_stage = Stage.CHOOSE_BUILD
  }

  reset() {
    this.active = false
    this.used = false
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

  get info(): GizmoInfo<Level> {
    return {
      type: this.type,
      id: this.id,
      level: this.level,
      energy_type: this.energy_type,
      energy_cost: this.energy_cost,
      value: this.value,
      effect: this.effect,
      active: this.active,
      used: this.used,
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

  get info(): GizmoInfo & GizmoPick {
    return {
      ...super.info,
      when_pick: this.when_pick,
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

  get info(): GizmoInfo & GizmoBuild {
    return {
      ...super.info,
      when_build: this.when_build,
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

  get info(): GizmoInfo & Required<GizmoUpgrade> {
    return {
      ...super.info,
      max_energy_num: this.max_energy_num,
      max_file_num: this.max_file_num,
      research_num: this.research_num,
      build_from_filed_cost_reduction: this.build_from_filed_cost_reduction,
      build_from_research_cost_reduction:
        this.build_from_research_cost_reduction,
    }
  }

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

export type ConverterFormula<E = EnergyWithAny> = {
  from: {
    energy: E
    num: number
  }
  to: {
    energy: E
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

  get info(): GizmoInfo & GizmoConverter {
    return {
      ...super.info,
      prerequisite: this.prerequisite,
      formulae: this.formulae,
    }
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

  get info(): GizmoInfo<Level> & GizmoFile {
    return super.info
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

export function is_upgrade_gizmo_info(
  gizmo: Gizmo<AllGizmoLevel>['info']
): gizmo is UpgradeGizmo['info'] {
  return gizmo.type === GizmoType.UPGRADE
}
export function is_converter_gizmo_info(
  gizmo: Gizmo<AllGizmoLevel>['info']
): gizmo is ConverterGizmo['info'] {
  return gizmo.type === GizmoType.CONVERTER
}
export function is_pick_gizmo_info(
  gizmo: Gizmo<AllGizmoLevel>['info']
): gizmo is PickGizmo['info'] {
  return gizmo.type === GizmoType.PICK
}
export function is_build_gizmo_info(
  gizmo: Gizmo<AllGizmoLevel>['info']
): gizmo is BuildGizmo['info'] {
  return gizmo.type === GizmoType.BUILD
}
export function is_file_gizmo_info(
  gizmo: Gizmo<AllGizmoLevel>['info']
): gizmo is FileGizmo['info'] {
  return gizmo.type === GizmoType.FILE
}
