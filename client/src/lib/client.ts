import type { Socket } from 'socket.io-client'
import { Stage, type Energy, type GizmoLevel } from 'gizmos-env/common'
import { init_energy_num } from 'gizmos-env/gizmos_utils'
import {
  ActionType,
  GizmosEnv,
  type Action,
  type Observation,
} from 'gizmos-env/GizmosEnv'
import type { PlayerInfo } from 'gizmos-env/Player'
import { derived, get, writable } from 'svelte/store'
import { connect_socket_as_player } from './helpers.js'

type PlayerList = {
  name: string
  index: number
  me: boolean
}[]

type RoomInfo = { name: string; ready: boolean }[]

export class GizmosClient {
  socket: Socket
  socket_status = writable<'green' | 'red' | 'pending'>('pending')

  room_info = writable<RoomInfo>([])
  game_ongoing = writable(false)

  player_list = writable<PlayerList>([])
  player_index = derived(
    this.player_list,
    player_list => player_list.find(p => p.me)?.index
  )

  login = (name: string) => {
    this.socket.emit('login', { name })
  }

  ready = () => {
    this.socket.emit('ready')
  }

  observation = writable<Observation | null>(null)
  env = writable<GizmosEnv | null>(null)
  drop_energy_num = writable(init_energy_num())

  me = derived(
    [this.observation, this.player_index],
    ([$observation, $player_index]): PlayerInfo | null => {
      if ($observation === null || $player_index === undefined) {
        return null
      }
      return $observation.players[$player_index]
    }
  )

  private step = (action: Action) => {
    this.socket.emit('action', action)
  }

  is_avail = derived([this.env, this.player_index], ([$env, $player_index]) => {
    const is_avail_map = Object.values(ActionType).reduce(
      (acc, curr) => ({ ...acc, [curr]: false }),
      {} as Record<ActionType, boolean>
    )
    if (!$env) return is_avail_map
    if ($player_index === undefined) return is_avail_map
    if ($env.state.curr_player_index !== $player_index) return is_avail_map
    $env.avail_actions.forEach(a => (is_avail_map[a] = true))
    return is_avail_map
  })

  pick = (index: number) => {
    if (!get(this.is_avail)[ActionType.PICK]) return
    this.step({ type: ActionType.PICK, index })
  }

  select_drop = (energy: Energy, num = 1) => {
    if (!get(this.is_avail)[ActionType.DROP]) return
    this.drop_energy_num.update(drop_energy_num => ({
      ...drop_energy_num,
      [energy]: drop_energy_num[energy] + num,
    }))
  }

  drop = () => {
    if (!get(this.is_avail)[ActionType.DROP]) return
    this.step({ type: ActionType.DROP, energy_num: get(this.drop_energy_num) })
    this.drop_energy_num.set(init_energy_num())
  }

  file = (level: GizmoLevel, index: number) => {
    if (!get(this.is_avail)[ActionType.FILE]) return
    this.step({ type: ActionType.FILE, level, index })
  }

  file_from_research = (index: number) => {
    if (!get(this.is_avail)[ActionType.FILE_FROM_RESEARCH]) return
    this.step({ type: ActionType.FILE_FROM_RESEARCH, index })
  }

  build = (
    level: GizmoLevel,
    index: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_index: number[]
  ) => {
    if (!get(this.is_avail)[ActionType.BUILD]) return
    this.step({
      type: ActionType.BUILD,
      level,
      index,
      cost_energy_num,
      cost_converter_gizmos_index,
    })
  }

  build_from_file = (
    index: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_index: number[]
  ) => {
    if (!get(this.is_avail)[ActionType.BUILD_FROM_FILED]) return
    this.step({
      type: ActionType.BUILD_FROM_FILED,
      index,
      cost_energy_num,
      cost_converter_gizmos_index,
    })
  }

  build_from_research = (
    index: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_index: number[]
  ) => {
    if (!get(this.is_avail)[ActionType.BUILD_FROM_RESEARCH]) return
    this.step({
      type: ActionType.BUILD_FROM_RESEARCH,
      index,
      cost_energy_num,
      cost_converter_gizmos_index,
    })
  }

  research = (level: GizmoLevel) => {
    if (!get(this.is_avail)[ActionType.RESEARCH]) return
    this.step({
      type: ActionType.RESEARCH,
      level,
    })
  }

  use_gizmo = (index: number) => {
    if (!get(this.is_avail)[ActionType.USE_GIZMO]) return
    this.step({ type: ActionType.USE_GIZMO, index })
  }

  use_gizmo_id = (id: number) => {
    const me = get(this.me)
    if (!me) {
      alert('not in game')
      return
    }
    const index = me.gizmos.findIndex(g => g.id === id)
    if (index < 0) {
      alert('unexpected gizmo used')
      return
    }
    this.use_gizmo(index)
  }

  give_up = () => {
    if (!get(this.is_avail)[ActionType.GIVE_UP]) return
    this.step({ type: ActionType.GIVE_UP })
  }

  end = () => {
    if (!get(this.is_avail)[ActionType.END]) return
    this.step({ type: ActionType.END })
  }

  destroy = () => {
    this.socket.disconnect()
  }

  constructor(socket?: Socket) {
    this.socket = socket ?? connect_socket_as_player()
    this.socket.on('room', (room_info: RoomInfo) => {
      this.room_info.set(room_info)
    })
    this.socket.on('observation', (observation: Observation) => {
      this.observation.set(observation)
      const new_env = new GizmosEnv(get(this.player_list).length)
      new_env.simulation(observation)
      this.env.set(new_env)
      if (observation.curr_stage === Stage.GAME_OVER) {
        if (observation.truncated) {
          alert('internal error')
          return
        }
        alert('GAME OVER!')
        alert(
          `Score:\n${observation.players
            .map((p, i) => `${get(this.player_list)[i].name}: ${p.score}`)
            .join('\n')}`
        )
      }
    })
    this.socket.on('start', (player_list: PlayerList) => {
      this.game_ongoing.set(true)
      this.player_list.set(player_list)
      this.socket.emit('observation')
    })
    this.socket.on('end', () => {
      this.game_ongoing.set(false)
      this.observation.set(null)
      this.env.set(null)
    })
    this.socket.on('error', msg => alert(msg))
    this.socket.on('connect', () => {
      console.log('[socket.connect]')
      this.socket_status.set('green')
    })
    this.socket.on('disconnect', reason => {
      console.error('[socket.disconnect]', reason)
      this.socket_status.set('red')
    })
    this.socket.on('connect_error', err => {
      console.error('[socket.connect_error]', err)
      this.socket_status.set('red')
    })
  }
}
