import {
  ALL_ENERGY_TYPES,
  type Energy,
  type GizmoLevel,
  Stage,
  BuildMethod,
  type AllGizmoLevel,
} from './common'
import { init_energy_pool } from './energy_pool'
import { init_gizmos } from './gizmos_pool'
import type { Gizmo, GizmoInfo } from './Gizmo'
import { Player, type PlayerInfo } from './Player'
import { random_int, sample, shuffle } from './utils'
import { init_energy_num } from './gizmos_utils'

function init_player(env: GizmosEnv, index: number) {
  return new Player({ env, index, gizmos: [env.u_gizmo(index)] })
}

type State = {
  curr_turn: number
  curr_stage: Stage
  curr_player_index: number
  is_last_turn: boolean
  energy_pool: Energy[]
  energy_board: Energy[]
  gizmos: Gizmo<AllGizmoLevel>[]
  gizmos_pool: Record<GizmoLevel, Gizmo[]>
  gizmos_board: Record<GizmoLevel, Gizmo[]>
  players: Player[]
  researching: null | {
    level: GizmoLevel
    gizmos: Gizmo[]
  }
  free_build: null | {
    level: GizmoLevel[]
  }
  free_pick_num: number
}

export enum ActionType {
  PICK = 'PICK',
  FILE = 'FILE',
  FILE_FROM_RESEARCH = 'FILE_FROM_RESEARCH',
  BUILD = 'BUILD',
  BUILD_FROM_RESEARCH = 'BUILD_FROM_RESEARCH',
  BUILD_FROM_FILED = 'BUILD_FROM_FILED',
  BUILD_FOR_FREE = 'BUILD_FOR_FREE',
  RESEARCH = 'RESEARCH',
  DROP = 'DROP',
  USE_GIZMO = 'USE_GIZMO',
  GIVE_UP = 'GIVE_UP',
  END = 'END',
}
export type Action =
  | { type: ActionType.PICK; index: number }
  | { type: ActionType.FILE; level: GizmoLevel; index: number }
  | { type: ActionType.FILE_FROM_RESEARCH; index: number }
  | {
      type: ActionType.BUILD
      level: GizmoLevel
      index: number
      cost_energy_num: Record<Energy, number>
      cost_converter_gizmos_index: number[]
    }
  | {
      type: ActionType.BUILD_FROM_FILED
      index: number
      cost_energy_num: Record<Energy, number>
      cost_converter_gizmos_index: number[]
    }
  | {
      type: ActionType.BUILD_FROM_RESEARCH
      index: number
      cost_energy_num: Record<Energy, number>
      cost_converter_gizmos_index: number[]
    }
  | {
      type: ActionType.BUILD_FOR_FREE
      level: GizmoLevel
      index: number
    }
  | {
      type: ActionType.RESEARCH
      level: GizmoLevel
    }
  | {
      type: ActionType.DROP
      energy_num: Record<Energy, number>
    }
  | {
      type: ActionType.USE_GIZMO
      index: number
    }
  | { type: ActionType.GIVE_UP }
  | { type: ActionType.END }

export type Observation = {
  curr_turn: State['curr_turn']
  curr_stage: State['curr_stage']
  curr_player_index: State['curr_player_index']
  is_last_turn: State['is_last_turn']
  energy_board: State['energy_board']
  gizmos_board: Record<GizmoLevel, GizmoInfo[]>
  researching: { level: GizmoLevel; gizmos: GizmoInfo[] } | null
  players: PlayerInfo[]
  avail_actions: ActionType[]
  free_build: State['free_build']
  free_pick_num: State['free_pick_num']
  truncated: boolean
}

export class GizmosEnv {
  player_num: number
  max_gizmos_num: number
  max_level3_gizmos_num: number

  state!: State

  pick_gizmos_from_pool(level: GizmoLevel, num: number) {
    const len = this.state.gizmos_pool[level].length
    return this.state.gizmos_pool[level].splice(0, Math.min(num, len))
  }

  drop_gizmos_to_pool(level: GizmoLevel, gizmos: Gizmo[]) {
    this.state.gizmos_pool[level] = [
      ...this.state.gizmos_pool[level],
      ...shuffle(gizmos),
    ]
  }

  pick_gizmo_from_board(level: GizmoLevel, index: number) {
    if (index >= this.state.gizmos_board[level].length) {
      throw new Error('gizmo index out of bound')
    }
    const gizmo = this.state.gizmos_board[level].splice(index, 1)[0]
    this.state.gizmos_board[level] = [
      ...this.state.gizmos_board[level],
      ...this.pick_gizmos_from_pool(level, 1),
    ]
    return gizmo
  }

  pick_energy_from_pool(num: number) {
    const len = this.state.energy_pool.length
    return this.state.energy_pool.splice(0, Math.min(num, len))
  }

  drop_energy_to_pool(energy_num: Record<Energy, number>) {
    const energy_list: Energy[] = []
    ALL_ENERGY_TYPES.forEach(energy => {
      for (let i = 0; i < energy_num[energy]; ++i) {
        energy_list.push(energy)
      }
    })

    this.state.energy_pool = shuffle([
      ...this.state.energy_pool,
      ...energy_list,
    ])
  }

  pick_energy_from_board(index: number) {
    if (index >= this.state.energy_board.length) {
      throw new Error('energy index out of bound')
    }
    const energy = this.state.energy_board.splice(index, 1)[0]
    this.state.energy_board = [
      ...this.state.energy_board,
      ...this.pick_energy_from_pool(1),
    ]
    return energy
  }

  pick_gizmo_from_research(index: number) {
    if (
      !this.state.researching ||
      index >= this.state.researching.gizmos.length
    ) {
      throw new Error('research index out of bound')
    }
    const gizmo = this.state.researching.gizmos.splice(index, 1)[0]
    this.drop_gizmos_to_pool(
      this.state.researching.level,
      this.state.researching.gizmos
    )
    this.state.researching = null
    return gizmo
  }

  gizmos_pool_len(level: GizmoLevel) {
    return this.state.gizmos_pool[level].length
  }

  energy_pool_len() {
    return this.state.energy_pool.length
  }

  get curr_player() {
    return this.state.players[this.state.curr_player_index]
  }

  get avail_actions() {
    let actions: ActionType[] = []
    switch (this.state.curr_stage) {
      case Stage.MAIN:
        actions = [ActionType.END]
        if (this.state.energy_board.length > 0) {
          actions.push(ActionType.PICK)
        }
        if (
          this.buildable_gizmos(this.all_board_gizmos, BuildMethod.DIRECTLY)
            .length > 0
        ) {
          actions.push(ActionType.BUILD)
        }
        if (this.curr_player.research_num > 0) {
          actions.push(ActionType.RESEARCH)
        }
        if (this.curr_player.filed.length < this.curr_player.max_file_num) {
          actions.push(ActionType.FILE)
        }
        if (
          this.curr_player.filed.length > 0 &&
          this.buildable_gizmos(this.curr_player.filed, BuildMethod.FROM_FILED)
            .length > 0
        ) {
          actions.push(ActionType.BUILD_FROM_FILED)
        }
        break
      case Stage.CHOOSE_BUILD:
        actions = [ActionType.GIVE_UP]
        if (this.state.free_build) {
          actions.push(ActionType.BUILD_FOR_FREE)
        } else if (
          this.buildable_gizmos(this.all_board_gizmos, BuildMethod.DIRECTLY)
            .length > 0
        ) {
          actions.push(ActionType.BUILD)
        }
        break
      case Stage.CHOOSE_FILE:
        actions = [ActionType.GIVE_UP]
        if (this.curr_player.filed.length < this.curr_player.max_file_num) {
          actions.push(ActionType.FILE)
        }
        break
      case Stage.CHOOSE_RESEARCH:
        actions = [ActionType.GIVE_UP]
        if (this.curr_player.research_num > 0) {
          actions.push(ActionType.RESEARCH)
        }
        break
      case Stage.RESEARCH:
        actions = [ActionType.GIVE_UP]
        if (
          this.buildable_gizmos(
            this.state.researching?.gizmos ?? [],
            BuildMethod.FROM_RESEARCH
          ).length > 0
        ) {
          actions.push(ActionType.BUILD_FROM_RESEARCH)
        }
        if (this.curr_player.filed.length < this.curr_player.max_file_num) {
          actions.push(ActionType.FILE_FROM_RESEARCH)
        }
        break
      case Stage.PICK:
        actions = [ActionType.END]
        if (this.state.energy_board.length > 0) {
          actions.push(ActionType.PICK)
        }
        break
      case Stage.DROP:
        actions = [ActionType.DROP]
        break
      case Stage.FREE:
        actions = [ActionType.END]
        if (this.curr_player.avail_gizmos.length > 0) {
          actions.push(ActionType.USE_GIZMO)
        }
        break
      case Stage.GAME_OVER:
        break
      default:
        throw new Error('unexpected stage')
    }
    return actions
  }

  get is_energy_overflow() {
    return this.curr_player.total_energy_num > this.curr_player.max_energy_num
  }

  pick(index: number) {
    if (!this.avail_actions.includes(ActionType.PICK)) {
      throw new Error('cannot pick now')
    }
    const energy = this.pick_energy_from_board(index)
    this.curr_player.pick(energy)
    this.state.curr_stage = Stage.FREE
  }

  file(level: GizmoLevel, index: number) {
    if (!this.avail_actions.includes(ActionType.FILE)) {
      throw new Error('cannot file now')
    }
    const gizmo = this.pick_gizmo_from_board(level, index)
    this.curr_player.file(gizmo)
    this.state.curr_stage = Stage.FREE
  }

  file_from_research(index: number) {
    if (!this.avail_actions.includes(ActionType.FILE_FROM_RESEARCH)) {
      throw new Error('cannot file_from_research now')
    }
    const gizmo = this.pick_gizmo_from_research(index)
    this.curr_player.file(gizmo)
    this.state.curr_stage = Stage.FREE
  }

  build(
    level: GizmoLevel,
    index: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_index: number[]
  ) {
    if (!this.avail_actions.includes(ActionType.BUILD)) {
      throw new Error('cannot build now')
    }
    const gizmo = this.pick_gizmo_from_board(level, index)
    this.curr_player.build(gizmo, cost_energy_num, cost_converter_gizmos_index)
    this.state.curr_stage = Stage.FREE
  }

  build_from_filed(
    index: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_index: number[]
  ) {
    if (!this.avail_actions.includes(ActionType.BUILD_FROM_FILED)) {
      throw new Error('cannot build_from_filed now')
    }
    this.curr_player.build_from_filed(
      index,
      cost_energy_num,
      cost_converter_gizmos_index
    )
    this.state.curr_stage = Stage.FREE
  }

  build_from_research(
    index: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_index: number[]
  ) {
    if (!this.avail_actions.includes(ActionType.BUILD_FROM_RESEARCH)) {
      throw new Error('cannot build_from_research now')
    }
    const gizmo = this.pick_gizmo_from_research(index)
    this.curr_player.build_from_research(
      gizmo,
      cost_energy_num,
      cost_converter_gizmos_index
    )
    this.state.curr_stage = Stage.FREE
  }

  build_for_free(level: GizmoLevel, index: number) {
    if (!this.avail_actions.includes(ActionType.BUILD_FOR_FREE)) {
      throw new Error('cannot build_for_free now')
    }
    if (
      !this.state.free_build ||
      !this.state.free_build.level.includes(level)
    ) {
      throw new Error('cannot build_for_free for this gizmo')
    }
    const gizmo = this.pick_gizmo_from_research(index)
    this.curr_player.build_for_free(gizmo)
    this.state.free_build = null
    this.state.curr_stage = Stage.FREE
  }

  research(level: GizmoLevel) {
    if (!this.avail_actions.includes(ActionType.RESEARCH)) {
      throw new Error('cannot research now')
    }
    this.state.researching = {
      level,
      gizmos: this.pick_gizmos_from_pool(level, this.curr_player.research_num),
    }
    this.state.curr_stage = Stage.RESEARCH
  }

  give_up() {
    if (!this.avail_actions.includes(ActionType.GIVE_UP)) {
      throw new Error('cannot give_up now')
    }
    switch (this.state.curr_stage) {
      case Stage.CHOOSE_BUILD:
        if (this.state.free_build) {
          this.state.free_build = null
        }
        break
      case Stage.CHOOSE_FILE:
      case Stage.CHOOSE_RESEARCH:
        break
      case Stage.RESEARCH:
        if (!this.state.researching) {
          throw new Error('no researching')
        }
        this.drop_gizmos_to_pool(
          this.state.researching.level,
          this.state.researching.gizmos
        )
        this.state.researching = null
        break
      default:
        throw new Error('give_up at an unexpected stage')
    }
    this.state.curr_stage = Stage.FREE
  }

  drop(energy_num: Record<Energy, number>) {
    if (!this.avail_actions.includes(ActionType.DROP)) {
      throw new Error('cannot drop now')
    }
    this.curr_player.drop(energy_num)
    this.state.curr_stage = Stage.FREE
  }

  use_gizmo(index: number) {
    if (!this.avail_actions.includes(ActionType.USE_GIZMO)) {
      throw new Error('cannot use_gizmo now')
    }
    this.curr_player.use_gizmo(index)
  }

  next_player() {
    if (
      this.curr_player.gizmos.length >= this.max_gizmos_num ||
      this.curr_player.level3_gizmos.length >= this.max_level3_gizmos_num
    ) {
      this.state.is_last_turn = true
    }
    if (this.state.curr_player_index + 1 >= this.state.players.length) {
      if (this.state.is_last_turn) {
        this.state.curr_stage = Stage.GAME_OVER
        return
      }
    }
    this.curr_player.reset_gizmos()
    this.state.curr_player_index =
      (this.state.curr_player_index + 1) % this.state.players.length
    this.state.curr_turn += 1
    this.state.curr_stage = Stage.MAIN
  }

  game_over() {
    return
  }

  truncated = false

  get_reward(playerIndex: number) {
    if (this.state.curr_stage !== Stage.GAME_OVER) return 0
    if (this.truncated) return -Infinity
    const score = this.state.players[playerIndex].score
    const rank =
      this.state.players.filter(player => player.score > score).length + 1
    const winner_reward = ((1 + this.player_num) * this.player_num) / 2
    const loser_reward = 1 - rank
    return rank === 1 ? winner_reward : loser_reward
  }

  step(playerIndex: number, action: Action) {
    try {
      if (playerIndex !== this.state.curr_player_index) {
        throw new Error('not your turn')
      }
      if (!this.avail_actions.includes(action.type)) {
        throw new Error('unexpected action type')
      }
      switch (action.type) {
        case ActionType.PICK:
          this.pick(action.index)
          break
        case ActionType.FILE:
          this.file(action.level, action.index)
          break
        case ActionType.FILE_FROM_RESEARCH:
          this.file_from_research(action.index)
          break
        case ActionType.BUILD:
          this.build(
            action.level,
            action.index,
            action.cost_energy_num,
            action.cost_converter_gizmos_index
          )
          break
        case ActionType.BUILD_FROM_FILED:
          this.build_from_filed(
            action.index,
            action.cost_energy_num,
            action.cost_converter_gizmos_index
          )
          break
        case ActionType.BUILD_FROM_RESEARCH:
          this.build_from_research(
            action.index,
            action.cost_energy_num,
            action.cost_converter_gizmos_index
          )
          break
        case ActionType.BUILD_FOR_FREE:
          this.build_for_free(action.level, action.index)
          break
        case ActionType.RESEARCH:
          this.research(action.level)
          break
        case ActionType.DROP:
          this.drop(action.energy_num)
          break
        case ActionType.USE_GIZMO:
          this.use_gizmo(action.index)
          break
        case ActionType.GIVE_UP:
          this.give_up()
          break
        case ActionType.END:
          this.next_player()
          return
        default:
          throw new Error('unexpected action type')
      }
      if (this.is_energy_overflow) {
        this.state.curr_stage = Stage.DROP
      } else if (this.state.free_pick_num > 0) {
        this.state.free_pick_num -= 1
        this.state.curr_stage = Stage.PICK
      } else {
        if (this.avail_actions.every(action => action === ActionType.END)) {
          this.next_player()
        }
      }
      if (this.state.curr_stage === Stage.GAME_OVER) {
        this.game_over()
      }
    } catch (e) {
      console.error(e)
      this.truncated = true
      this.state.curr_stage = Stage.GAME_OVER
    }
  }

  u_gizmo(id: number) {
    return this.state.gizmos[id]
  }

  gizmo(id: number) {
    const gizmo = this.u_gizmo(id)
    if (gizmo.level === 0) {
      throw new Error('unexpected gizmo')
    }
    return gizmo as Gizmo
  }

  observation(playerIndex?: number): Observation {
    const is_curr_player = playerIndex === this.state.curr_player_index
    return {
      curr_turn: this.state.curr_turn,
      curr_stage: this.state.curr_stage,
      curr_player_index: this.state.curr_player_index,
      is_last_turn: this.state.is_last_turn,
      energy_board: this.state.energy_board,
      gizmos_board: {
        1: this.state.gizmos_board[1].map(g => g.info),
        2: this.state.gizmos_board[2].map(g => g.info),
        3: this.state.gizmos_board[3].map(g => g.info),
      },
      researching: is_curr_player
        ? this.state.researching
          ? {
              level: this.state.researching.level,
              gizmos: this.state.researching.gizmos.map(g => g.info),
            }
          : null
        : null,
      players: this.state.players.map(p => p.info),
      avail_actions: this.avail_actions,
      free_build: this.state.free_build,
      free_pick_num: this.state.free_pick_num,
      truncated: this.truncated,
    }
  }

  sim_u_gizmo = (info: GizmoInfo<AllGizmoLevel>) => {
    const gizmo = this.u_gizmo(info.id)
    gizmo.used = info.used
    gizmo.active = info.active
    return gizmo
  }

  sim_gizmo = (info: GizmoInfo) => {
    const gizmo = this.gizmo(info.id)
    gizmo.used = info.used
    gizmo.active = info.active
    return gizmo
  }

  simulation = (observation: Observation) => {
    const gizmos = this.state.gizmos
    this.state = {
      ...observation,
      energy_pool: [],
      gizmos,
      gizmos_pool: { 1: [], 2: [], 3: [] },
      gizmos_board: {
        1: observation.gizmos_board[1].map(this.sim_gizmo),
        2: observation.gizmos_board[2].map(this.sim_gizmo),
        3: observation.gizmos_board[3].map(this.sim_gizmo),
      },
      players: observation.players.map((p, i) => {
        return new Player({
          ...p,
          env: this,
          index: i,
          gizmos: p.gizmos.map(this.sim_u_gizmo),
          filed: p.filed.map(this.sim_gizmo),
        })
      }),
      researching: observation.researching
        ? {
            level: observation.researching.level,
            gizmos: observation.researching.gizmos.map(this.sim_gizmo),
          }
        : null,
    }
  }

  reset() {
    this.state = {
      curr_turn: 1,
      curr_stage: Stage.MAIN,
      curr_player_index: 0,
      is_last_turn: false,
      energy_pool: init_energy_pool(),
      energy_board: [],
      ...init_gizmos(),
      gizmos_board: {
        1: [],
        2: [],
        3: [],
      },
      players: [],
      researching: null,
      free_build: null,
      free_pick_num: 0,
    }
    this.state.energy_board = this.pick_energy_from_pool(6)
    this.state.gizmos_board[1] = this.pick_gizmos_from_pool(1, 4)
    this.state.gizmos_board[2] = this.pick_gizmos_from_pool(2, 3)
    this.state.gizmos_board[3] = this.pick_gizmos_from_pool(3, 2)
    for (let i = 0; i < this.player_num; ++i) {
      this.state.players.push(init_player(this, i))
    }
  }

  build_solutions(
    gizmo_like: Gizmo | number,
    method: BuildMethod,
    check_only?: boolean
  ) {
    const player = this.curr_player
    const gizmo =
      typeof gizmo_like === 'number' ? this.gizmo(gizmo_like) : gizmo_like

    return player.build_solutions(
      gizmo,
      method,
      player.energy_num,
      player.converter_gizmos.filter(g => g.is_satisfied(gizmo)),
      check_only
    )
  }

  can_build(gizmo: Gizmo, method: BuildMethod) {
    return this.build_solutions(gizmo, method, true).length > 0
  }

  buildable_gizmos(gizmos: Gizmo[], method: BuildMethod) {
    return gizmos.filter(g => this.can_build(g, method))
  }

  get all_board_gizmos() {
    return [
      ...this.state.gizmos_board[1],
      ...this.state.gizmos_board[2],
      ...this.state.gizmos_board[3],
    ]
  }

  sample_pick(): Action {
    return {
      type: ActionType.PICK,
      index: random_int(this.state.energy_board.length),
    }
  }

  private sample_board_gizmo(gizmos = this.all_board_gizmos) {
    const gizmo = sample(gizmos)
    const level = gizmo.level
    const index = this.state.gizmos_board[level].indexOf(gizmo)
    return { level, index }
  }

  private sample_solution(gizmo: Gizmo, method: BuildMethod) {
    const solutions = this.build_solutions(gizmo, method)
    return sample(solutions)
  }

  sample_file(): Action {
    return {
      type: ActionType.FILE,
      ...this.sample_board_gizmo(),
    }
  }

  sample_file_from_research(): Action {
    const researching = this.state.researching
    if (!researching) {
      throw new Error('sample_file_from_research failed')
    }
    return {
      type: ActionType.FILE_FROM_RESEARCH,
      index: random_int(researching.gizmos.length),
    }
  }

  sample_build(): Action {
    const avail_gizmos = this.all_board_gizmos.filter(g =>
      this.can_build(g, BuildMethod.DIRECTLY)
    )
    if (avail_gizmos.length <= 0) {
      throw new Error('sample_build failed')
    }
    const { level, index } = this.sample_board_gizmo(avail_gizmos)
    const gizmo = this.state.gizmos_board[level][index]
    const { energy_num: cost_energy_num, gizmos: cost_converter_gizmos } =
      this.sample_solution(gizmo, BuildMethod.DIRECTLY)
    const cost_converter_gizmos_index = cost_converter_gizmos.map(g =>
      this.curr_player.gizmos.indexOf(g)
    )
    return {
      type: ActionType.BUILD,
      level,
      index,
      cost_energy_num,
      cost_converter_gizmos_index,
    }
  }

  sample_build_from_research(): Action {
    const researching_gizmos = this.state.researching?.gizmos ?? []
    const avail_gizmos = researching_gizmos.filter(g =>
      this.can_build(g, BuildMethod.FROM_RESEARCH)
    )
    if (avail_gizmos.length <= 0) {
      throw new Error('sample_build_from_research failed')
    }
    const gizmo = sample(avail_gizmos)
    const index = researching_gizmos.indexOf(gizmo)
    const { energy_num: cost_energy_num, gizmos: cost_converter_gizmos } =
      this.sample_solution(gizmo, BuildMethod.FROM_RESEARCH)
    const cost_converter_gizmos_index = cost_converter_gizmos.map(g =>
      this.curr_player.gizmos.indexOf(g)
    )
    return {
      type: ActionType.BUILD_FROM_RESEARCH,
      index,
      cost_energy_num,
      cost_converter_gizmos_index,
    }
  }

  sample_build_from_file(): Action {
    const avail_gizmos = this.curr_player.filed.filter(g =>
      this.can_build(g, BuildMethod.FROM_FILED)
    )
    if (avail_gizmos.length <= 0) {
      throw new Error('sample_build_from_research failed')
    }
    const gizmo = sample(avail_gizmos)
    const index = this.curr_player.filed.indexOf(gizmo)
    const { energy_num: cost_energy_num, gizmos: cost_converter_gizmos } =
      this.sample_solution(gizmo, BuildMethod.FROM_FILED)
    const cost_converter_gizmos_index = cost_converter_gizmos.map(g =>
      this.curr_player.gizmos.indexOf(g)
    )
    return {
      type: ActionType.BUILD_FROM_FILED,
      index,
      cost_energy_num,
      cost_converter_gizmos_index,
    }
  }

  sample_build_for_free(): Action {
    const levels = this.state.free_build?.level ?? []
    const avail_gizmos = levels.reduce(
      (acc, curr) => [...acc, ...this.state.gizmos_board[curr]],
      [] as Gizmo[]
    )
    if (avail_gizmos.length <= 0) {
      throw new Error('sample_build_for_free failed')
    }
    const { level, index } = this.sample_board_gizmo(avail_gizmos)
    return {
      type: ActionType.BUILD_FOR_FREE,
      level,
      index,
    }
  }

  sample_research(): Action {
    const levels: GizmoLevel[] = [1, 2, 3]
    const avail_levels = levels.filter(
      level => this.state.gizmos_pool[level].length > 0
    )
    const level = sample(avail_levels)
    return {
      type: ActionType.RESEARCH,
      level,
    }
  }

  sample_drop(): Action {
    const should_drop_num =
      this.curr_player.total_energy_num - this.curr_player.max_energy_num
    const energy = shuffle(
      ALL_ENERGY_TYPES.reduce(
        (acc, curr) => [
          ...acc,
          ...new Array(this.curr_player.info.energy_num[curr]).fill(curr),
        ],
        [] as Energy[]
      )
    )
    const drop_energy = energy.splice(0, should_drop_num)
    const drop_energy_num = drop_energy.reduce(
      (acc, curr) => ({
        ...acc,
        [curr]: acc[curr] + 1,
      }),
      init_energy_num()
    )
    return {
      type: ActionType.DROP,
      energy_num: drop_energy_num,
    }
  }

  sample_use_gizmo(): Action {
    const gizmo = sample(this.curr_player.avail_gizmos)
    const index = this.curr_player.gizmos.indexOf(gizmo)
    return {
      type: ActionType.USE_GIZMO,
      index,
    }
  }

  sample(): Action {
    const action_type = sample(this.avail_actions)
    switch (action_type) {
      case ActionType.PICK:
        return this.sample_pick()
      case ActionType.FILE:
        return this.sample_file()
      case ActionType.FILE_FROM_RESEARCH:
        return this.sample_file_from_research()
      case ActionType.BUILD:
        return this.sample_build()
      case ActionType.BUILD_FROM_RESEARCH:
        return this.sample_build_from_research()
      case ActionType.BUILD_FROM_FILED:
        return this.sample_build_from_file()
      case ActionType.BUILD_FOR_FREE:
        return this.sample_build_for_free()
      case ActionType.RESEARCH:
        return this.sample_research()
      case ActionType.DROP:
        return this.sample_drop()
      case ActionType.USE_GIZMO:
        return this.sample_use_gizmo()
      case ActionType.GIVE_UP:
        return { type: ActionType.GIVE_UP }
      case ActionType.END:
        return { type: ActionType.END }
    }
  }

  constructor(player_num = 2, max_gizmos_num = 16, max_level3_gizmos_num = 4) {
    if (player_num < 2 || max_gizmos_num < 2 || max_level3_gizmos_num < 1) {
      throw new Error('unsupported configuration')
    }
    this.player_num = player_num
    this.max_gizmos_num = max_gizmos_num
    this.max_level3_gizmos_num = max_level3_gizmos_num
    this.reset()
  }
}
