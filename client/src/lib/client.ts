import type { Socket } from 'socket.io-client'
import { Stage, type Energy, type GizmoLevel } from 'gizmos-env/common'
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
  pending = writable(false)

  private name = writable('')
  room_info = writable<RoomInfo>([])
  in_room = derived([this.name, this.room_info], ([$name, $room_info]) => {
    return $room_info.some(({ name }) => name === $name)
  })
  game_ongoing = writable(false)

  player_list = writable<PlayerList>([])
  player_index = derived(
    this.player_list,
    player_list => player_list.find(p => p.me)?.index
  )

  log = writable<string[]>([])

  login = (name: string) => {
    // FIXME: not robust to get name here
    this.name.set(name)
    this.socket.emit('login', { name })
  }

  ready = () => {
    this.socket.emit('ready')
  }

  observation = writable<Observation | null>(null)
  env = writable<GizmosEnv | null>(null)

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
    this.pending.set(true)
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

  pick = (energy: Energy) => {
    if (!get(this.is_avail)[ActionType.PICK]) return
    this.step({ type: ActionType.PICK, energy })
  }

  file = (id: number) => {
    if (!get(this.is_avail)[ActionType.FILE]) return
    this.step({ type: ActionType.FILE, id })
  }

  file_from_research = (id: number) => {
    if (!get(this.is_avail)[ActionType.FILE_FROM_RESEARCH]) return
    this.step({ type: ActionType.FILE_FROM_RESEARCH, id })
  }

  build = (
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) => {
    if (!get(this.is_avail)[ActionType.BUILD]) return
    this.step({
      type: ActionType.BUILD,
      id,
      cost_energy_num,
      cost_converter_gizmos_id,
    })
  }

  build_from_filed = (
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) => {
    if (!get(this.is_avail)[ActionType.BUILD_FROM_FILED]) return
    this.step({
      type: ActionType.BUILD_FROM_FILED,
      id,
      cost_energy_num,
      cost_converter_gizmos_id,
    })
  }

  build_from_research = (
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) => {
    if (!get(this.is_avail)[ActionType.BUILD_FROM_RESEARCH]) return
    this.step({
      type: ActionType.BUILD_FROM_RESEARCH,
      id,
      cost_energy_num,
      cost_converter_gizmos_id,
    })
  }

  research = (level: GizmoLevel) => {
    if (!get(this.is_avail)[ActionType.RESEARCH]) return
    this.step({
      type: ActionType.RESEARCH,
      level,
    })
  }

  use_gizmo = (id: number) => {
    if (!get(this.is_avail)[ActionType.USE_GIZMO]) return
    this.step({ type: ActionType.USE_GIZMO, id })
  }

  give_up = () => {
    if (!get(this.is_avail)[ActionType.GIVE_UP]) return
    this.step({ type: ActionType.GIVE_UP })
  }

  end = () => {
    if (!get(this.is_avail)[ActionType.END]) return
    this.step({ type: ActionType.END })
  }

  sample = () => {
    const env = get(this.env)
    if (!env) return
    const action = env.sample()
    this.step(action)
    return action
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
      const new_env = new GizmosEnv({
        player_num: get(this.player_list).length,
      })
      new_env.simulation(observation)
      this.env.set(new_env)
      this.pending.set(false)
      if (observation.curr_stage === Stage.GAME_OVER) {
        if (observation.truncated) {
          alert('internal error')
          return
        }
        this.log.update(log => {
          log.push('GAME OVER!')
          log.push('Score:')
          observation.players.forEach((p, i) =>
            log.push(`${get(this.player_list)[i].name}: ${p.score}`)
          )
          return log
        })
      }
    })
    this.socket.on(
      'action',
      ({ name, action }: { name: string; action: Action }) => {
        this.log.update(log => {
          log.push(`${name}: ${JSON.stringify(action)}`)
          return log
        })
      }
    )
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
