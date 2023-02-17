import {
  ALL_ENERGY_TYPES,
  type Energy,
  type GizmoLevel,
  Stage,
  BuildMethod,
  type AllGizmoLevel,
} from './common'
import { init_energy_pool } from './energy_pool'
import {
  init_gizmos,
  init_level1,
  init_level2,
  init_level3,
} from './gizmos_pool'
import type { Gizmo, GizmoInfo } from './Gizmo'
import { Player, type PlayerInfo } from './Player'
import { sample, shuffle } from './utils'

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
  CHOOSE_TRIGGER = 'CHOOSE_TRIGGER',
  USE_GIZMO = 'USE_GIZMO',
  GIVE_UP = 'GIVE_UP',
  END = 'END',
}
export type ActionBuildSolution = {
  id: number
  cost_energy_num: Record<Energy, number>
  cost_converter_gizmos_id: number[]
}
export type Action =
  | { type: ActionType.PICK; energy: Energy }
  | { type: ActionType.FILE; id: number }
  | { type: ActionType.FILE_FROM_RESEARCH; id: number }
  | ({ type: ActionType.BUILD } & ActionBuildSolution)
  | ({ type: ActionType.BUILD_FROM_FILED } & ActionBuildSolution)
  | ({ type: ActionType.BUILD_FROM_RESEARCH } & ActionBuildSolution)
  | { type: ActionType.BUILD_FOR_FREE; id: number }
  | { type: ActionType.RESEARCH; level: GizmoLevel }
  | { type: ActionType.CHOOSE_TRIGGER; gizmos: number[] }
  | { type: ActionType.USE_GIZMO; id: number }
  | { type: ActionType.GIVE_UP }
  | { type: ActionType.END }

export type Observation = {
  curr_turn: State['curr_turn']
  curr_stage: State['curr_stage']
  curr_player_index: State['curr_player_index']
  is_last_turn: State['is_last_turn']
  energy_pool_num: number
  energy_board: State['energy_board']
  gizmos_pool_num: Record<GizmoLevel, number>
  gizmos_board: Record<GizmoLevel, GizmoInfo[]>
  researching: { level: GizmoLevel; gizmos: GizmoInfo[] } | null
  players: PlayerInfo[]
  free_build: State['free_build']
  free_pick_num: State['free_pick_num']
  truncated: boolean
}

export class GizmosEnv {
  check: boolean

  player_num: number
  max_gizmos_num: number
  max_level3_gizmos_num: number

  state!: State

  draw_gizmos_from_pool(level: GizmoLevel, num: number) {
    const len = this.state.gizmos_pool[level].length
    return this.state.gizmos_pool[level].splice(0, Math.min(num, len))
  }

  drop_gizmos_to_pool(level: GizmoLevel, gizmos: Gizmo[]) {
    this.state.gizmos_pool[level] = [
      ...this.state.gizmos_pool[level],
      ...shuffle(gizmos),
    ]
  }

  pick_gizmo_from_board(id: number) {
    const gizmo = this.all_board_gizmos.find(g => g.id === id)
    if (!gizmo) {
      throw new Error('[pick_gizmo_from_board] no such gizmo')
    }
    this.state.gizmos_board[gizmo.level] = [
      ...this.state.gizmos_board[gizmo.level].filter(g => g.id !== id),
      ...this.draw_gizmos_from_pool(gizmo.level, 1),
    ]
    return gizmo
  }

  draw_energy_from_pool(num: number) {
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

  pick_energy_from_board(energy: Energy) {
    const index = this.state.energy_board.indexOf(energy)
    if (index === -1) {
      throw new Error('[pick_energy_from_board] no such energy')
    }
    this.state.energy_board.splice(index, 1)
    this.state.energy_board = [
      ...this.state.energy_board,
      ...this.draw_energy_from_pool(1),
    ]
    return energy
  }

  pick_gizmo_from_research(id: number) {
    if (!this.state.researching) {
      throw new Error('[pick_gizmo_from_research] not researching')
    }
    const index = this.state.researching.gizmos.findIndex(g => g.id === id)
    if (index === -1) {
      throw new Error('[pick_gizmo_from_research] no such gizmo')
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
    let actions: Set<ActionType> = new Set()
    switch (this.state.curr_stage) {
      case Stage.MAIN:
        actions.add(ActionType.END)
        if (this.state.energy_board.length > 0) {
          actions.add(ActionType.PICK)
        }
        if (
          this.buildable_gizmos(this.all_board_gizmos, BuildMethod.DIRECTLY)
            .length > 0
        ) {
          actions.add(ActionType.BUILD)
        }
        if (this.curr_player.research_num > 0) {
          actions.add(ActionType.RESEARCH)
        }
        if (this.curr_player.filed.size < this.curr_player.max_file_num) {
          actions.add(ActionType.FILE)
        }
        if (
          this.curr_player.filed.size > 0 &&
          this.buildable_gizmos(this.curr_player.filed, BuildMethod.FROM_FILED)
            .length > 0
        ) {
          actions.add(ActionType.BUILD_FROM_FILED)
        }
        break
      case Stage.RESEARCH:
        actions.add(ActionType.GIVE_UP)
        if (
          this.buildable_gizmos(
            this.state.researching?.gizmos ?? [],
            BuildMethod.FROM_RESEARCH
          ).length > 0
        ) {
          actions.add(ActionType.BUILD_FROM_RESEARCH)
        }
        if (this.curr_player.filed.size < this.curr_player.max_file_num) {
          actions.add(ActionType.FILE_FROM_RESEARCH)
        }
        break
      case Stage.TRIGGER:
        actions.add(ActionType.END)
        if (this.curr_player.avail_gizmos.length > 0) {
          actions.add(ActionType.USE_GIZMO)
        }
        break
      case Stage.EXTRA_PICK:
        actions.add(ActionType.GIVE_UP)
        if (this.state.energy_board.length > 0) {
          actions.add(ActionType.PICK)
        }
        break
      case Stage.EXTRA_BUILD:
        actions.add(ActionType.GIVE_UP)
        if (this.state.free_build) {
          actions.add(ActionType.BUILD_FOR_FREE)
        } else if (
          this.buildable_gizmos(this.all_board_gizmos, BuildMethod.DIRECTLY)
            .length > 0
        ) {
          actions.add(ActionType.BUILD)
        }
        break
      case Stage.EXTRA_FILE:
        actions.add(ActionType.GIVE_UP)
        if (this.curr_player.filed.size < this.curr_player.max_file_num) {
          actions.add(ActionType.FILE)
        }
        break
      case Stage.EXTRA_RESEARCH:
        actions.add(ActionType.GIVE_UP)
        if (this.curr_player.research_num > 0) {
          actions.add(ActionType.RESEARCH)
        }
        break
      case Stage.GAME_OVER:
        break
      default:
        throw new Error('[avail_actions] unexpected stage')
    }
    return actions
  }

  private action_avail(action: ActionType) {
    if (!this.check) return true
    return this.avail_actions.has(action)
  }

  pick(energy: Energy) {
    this.pick_energy_from_board(energy)
    this.curr_player.pick(energy)
    this.state.curr_stage = Stage.TRIGGER
  }

  file(id: number) {
    const gizmo = this.pick_gizmo_from_board(id)
    this.curr_player.file(gizmo)
    this.state.curr_stage = Stage.TRIGGER
  }

  file_from_research(id: number) {
    const gizmo = this.pick_gizmo_from_research(id)
    this.curr_player.file(gizmo)
    this.state.curr_stage = Stage.TRIGGER
  }

  build(
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) {
    const gizmo = this.pick_gizmo_from_board(id)
    this.curr_player.build(gizmo, cost_energy_num, cost_converter_gizmos_id)
    this.state.curr_stage = Stage.TRIGGER
  }

  build_from_filed(
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) {
    this.curr_player.build_from_filed(
      id,
      cost_energy_num,
      cost_converter_gizmos_id
    )
    this.state.curr_stage = Stage.TRIGGER
  }

  build_from_research(
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) {
    const gizmo = this.pick_gizmo_from_research(id)
    this.curr_player.build_from_research(
      gizmo,
      cost_energy_num,
      cost_converter_gizmos_id
    )
    this.state.curr_stage = Stage.TRIGGER
  }

  build_for_free(id: number) {
    if (!this.state.free_build) {
      throw new Error('[build_for_free] no free build')
    }
    const gizmo = this.pick_gizmo_from_research(id)
    if (!this.state.free_build.level.includes(gizmo.level)) {
      throw new Error('[build_for_free] wrong level')
    }
    this.curr_player.build_for_free(gizmo)
    this.state.free_build = null
    this.state.curr_stage = Stage.TRIGGER
  }

  research(level: GizmoLevel) {
    this.state.researching = {
      level,
      gizmos: this.draw_gizmos_from_pool(level, this.curr_player.research_num),
    }
    this.state.curr_stage = Stage.RESEARCH
  }

  give_up() {
    switch (this.state.curr_stage) {
      case Stage.EXTRA_PICK:
        this.state.free_pick_num = 0
        break
      case Stage.EXTRA_BUILD:
        if (this.state.free_build) {
          this.state.free_build = null
        }
        break
      case Stage.EXTRA_FILE:
      case Stage.EXTRA_RESEARCH:
        break
      case Stage.RESEARCH:
        if (!this.state.researching) {
          throw new Error('[give_up] no researching')
        }
        this.drop_gizmos_to_pool(
          this.state.researching.level,
          this.state.researching.gizmos
        )
        this.state.researching = null
        break
      default:
        throw new Error('[give_up] unexpected stage')
    }
    this.state.curr_stage = Stage.TRIGGER
  }

  use_gizmo(id: number) {
    if (!this.action_avail(ActionType.USE_GIZMO)) {
      throw new Error('[use_gizmo] unavailable')
    }
    this.curr_player.use_gizmo(id)
  }

  next_player() {
    if (
      this.curr_player.gizmos.size >= this.max_gizmos_num ||
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
    console.log('[step]', { playerIndex }, action)
    console.time('step')
    try {
      if (playerIndex !== this.state.curr_player_index) {
        console.error('[step] not your turn')
        return
      }
      if (!this.action_avail(action.type)) {
        console.error(`[step] action ${action.type} unavailable`)
        return
      }
      switch (action.type) {
        case ActionType.PICK:
          this.pick(action.energy)
          break
        case ActionType.FILE:
          this.file(action.id)
          break
        case ActionType.FILE_FROM_RESEARCH:
          this.file_from_research(action.id)
          break
        case ActionType.BUILD:
          this.build(
            action.id,
            action.cost_energy_num,
            action.cost_converter_gizmos_id
          )
          break
        case ActionType.BUILD_FROM_FILED:
          this.build_from_filed(
            action.id,
            action.cost_energy_num,
            action.cost_converter_gizmos_id
          )
          break
        case ActionType.BUILD_FROM_RESEARCH:
          this.build_from_research(
            action.id,
            action.cost_energy_num,
            action.cost_converter_gizmos_id
          )
          break
        case ActionType.BUILD_FOR_FREE:
          this.build_for_free(action.id)
          break
        case ActionType.RESEARCH:
          this.research(action.level)
          break
        case ActionType.USE_GIZMO:
          this.use_gizmo(action.id)
          break
        case ActionType.GIVE_UP:
          this.give_up()
          break
        case ActionType.END:
          this.next_player()
          return
        default:
          console.error('[step] unexpected action type')
          return
      }
      if (this.state.free_pick_num > 0) {
        this.state.free_pick_num -= 1
        this.state.curr_stage = Stage.EXTRA_PICK
      } else {
        if (
          this.avail_actions.size <= 0 ||
          (this.avail_actions.size === 1 &&
            this.avail_actions.has(ActionType.END))
        ) {
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
    console.timeEnd('step')
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
      energy_pool_num: this.energy_pool_len(),
      energy_board: this.state.energy_board,
      gizmos_pool_num: {
        1: this.gizmos_pool_len(1),
        2: this.gizmos_pool_len(2),
        3: this.gizmos_pool_len(3),
      },
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
      energy_pool: ['red', 'blue', 'yellow', 'black'],
      gizmos,
      gizmos_pool: { 1: init_level1(), 2: init_level2(), 3: init_level3() },
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
    this.state.energy_board = this.draw_energy_from_pool(6)
    this.state.gizmos_board[1] = this.draw_gizmos_from_pool(1, 4)
    this.state.gizmos_board[2] = this.draw_gizmos_from_pool(2, 3)
    this.state.gizmos_board[3] = this.draw_gizmos_from_pool(3, 2)
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
      [...player.converter_gizmos].filter(g => g.is_satisfied(gizmo)),
      check_only
    )
  }

  can_build(gizmo: Gizmo, method: BuildMethod) {
    return this.build_solutions(gizmo, method, true).length > 0
  }

  buildable_gizmos(gizmos: Gizmo[] | Set<Gizmo>, method: BuildMethod) {
    return [...gizmos].filter(g => this.can_build(g, method))
  }

  get all_board_gizmos() {
    return [
      ...this.state.gizmos_board[1],
      ...this.state.gizmos_board[2],
      ...this.state.gizmos_board[3],
    ]
  }

  get space_pick(): Action[] {
    if (![Stage.MAIN, Stage.EXTRA_PICK].includes(this.state.curr_stage)) {
      return []
    }
    if (!this.curr_player.can_add_energy) {
      return []
    }
    return this.state.energy_board.map(energy => ({
      type: ActionType.PICK,
      energy,
    }))
  }

  get space_file(): Action[] {
    if (![Stage.MAIN, Stage.EXTRA_FILE].includes(this.state.curr_stage)) {
      return []
    }
    if (!this.curr_player.can_file) {
      return []
    }
    return this.all_board_gizmos.map(gizmo => ({
      type: ActionType.FILE,
      id: gizmo.id,
    }))
  }

  get space_file_from_research(): Action[] {
    if (this.state.curr_stage !== Stage.RESEARCH) {
      return []
    }
    const researching = this.state.researching
    if (!researching) {
      return []
    }
    if (!this.curr_player.can_file) {
      return []
    }
    return researching.gizmos.map(gizmo => ({
      type: ActionType.FILE_FROM_RESEARCH,
      id: gizmo.id,
    }))
  }

  private space_build(
    gizmos: Gizmo[] | Set<Gizmo>,
    method: BuildMethod,
    action_type:
      | ActionType.BUILD
      | ActionType.BUILD_FROM_FILED
      | ActionType.BUILD_FROM_RESEARCH
  ): Action[] {
    let actions: Action[] = []
    ;[...gizmos].forEach(gizmo => {
      this.build_solutions(gizmo, method).forEach(solution => {
        actions.push({
          type: action_type,
          id: gizmo.id,
          cost_energy_num: solution.energy_num,
          cost_converter_gizmos_id: solution.gizmos.map(g => g.id),
        })
      })
    })
    return actions
  }

  get space_build_directly(): Action[] {
    if (![Stage.MAIN, Stage.EXTRA_BUILD].includes(this.state.curr_stage)) {
      return []
    }
    return this.space_build(
      this.all_board_gizmos,
      BuildMethod.DIRECTLY,
      ActionType.BUILD
    )
  }

  get space_build_from_file(): Action[] {
    if (this.state.curr_stage !== Stage.MAIN) {
      return []
    }
    return this.space_build(
      this.curr_player.filed,
      BuildMethod.FROM_FILED,
      ActionType.BUILD_FROM_FILED
    )
  }

  get space_build_from_research(): Action[] {
    if (this.state.curr_stage !== Stage.RESEARCH) {
      return []
    }
    const researching_gizmos = this.state.researching?.gizmos ?? []
    return this.space_build(
      researching_gizmos,
      BuildMethod.FROM_RESEARCH,
      ActionType.BUILD_FROM_RESEARCH
    )
  }

  get space_build_for_free(): Action[] {
    if (this.state.curr_stage !== Stage.EXTRA_BUILD) {
      return []
    }
    const levels = this.state.free_build?.level ?? []
    const avail_gizmos = levels.reduce(
      (acc, curr) => [...acc, ...this.state.gizmos_board[curr]],
      [] as Gizmo[]
    )
    return avail_gizmos.map(gizmo => ({
      type: ActionType.BUILD_FOR_FREE,
      id: gizmo.id,
    }))
  }

  get space_research(): Action[] {
    if (![Stage.MAIN, Stage.EXTRA_RESEARCH].includes(this.state.curr_stage)) {
      return []
    }
    const levels: GizmoLevel[] = [1, 2, 3]
    const avail_levels = levels.filter(
      level => this.state.gizmos_pool[level].length > 0
    )
    return avail_levels.map(level => ({
      type: ActionType.RESEARCH,
      level,
    }))
  }

  get space_use_gizmo(): Action[] {
    if (this.state.curr_stage !== Stage.TRIGGER) {
      return []
    }
    return this.curr_player.avail_gizmos.map(gizmo => ({
      type: ActionType.USE_GIZMO,
      id: gizmo.id,
    }))
  }

  get space_give_up(): Action[] {
    if (
      ![
        Stage.EXTRA_PICK,
        Stage.EXTRA_BUILD,
        Stage.EXTRA_FILE,
        Stage.EXTRA_RESEARCH,
        Stage.RESEARCH,
      ].includes(this.state.curr_stage)
    ) {
      return []
    }
    return [{ type: ActionType.GIVE_UP }]
  }

  get space_end(): Action[] {
    if (![Stage.MAIN, Stage.TRIGGER].includes(this.state.curr_stage)) {
      return []
    }
    return [{ type: ActionType.END }]
  }

  get action_space(): Action[] {
    return [
      ...this.space_pick,
      ...this.space_file,
      ...this.space_file_from_research,
      ...this.space_build_directly,
      ...this.space_build_from_file,
      ...this.space_build_from_research,
      ...this.space_build_for_free,
      ...this.space_research,
      ...this.space_use_gizmo,
      ...this.space_give_up,
      ...this.space_end,
    ]
  }

  sample(): Action {
    return sample(this.action_space)
  }

  constructor({
    player_num = 2,
    max_gizmos_num = 16,
    max_level3_gizmos_num = 4,
    check = true,
  }) {
    if (player_num < 1 || max_gizmos_num < 2 || max_level3_gizmos_num < 1) {
      throw new Error('unsupported configuration')
    }
    this.check = check
    this.player_num = player_num
    this.max_gizmos_num = max_gizmos_num
    this.max_level3_gizmos_num = max_level3_gizmos_num
    this.reset()
  }
}
