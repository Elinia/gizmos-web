import type { Socket } from 'socket.io-client'
import type { Energy, GizmoLevel } from 'gizmos-env/common'
import { ActionType, type Action, type Observation } from 'gizmos-env/GizmosEnv'
import { derived, get, writable } from 'svelte/store'
import {
  connect_socket_as_player,
  connect_socket_as_observer,
} from './helpers.js'
import { GizmosGame } from './game.js'
import type { ActionLog, PlayerList, Replay } from './types.js'

type RoomInfo = { name: string; ready: boolean }[]

export class GizmosClient {
  socket: Socket | null = null
  socket_status = writable<'green' | 'red' | 'pending'>('pending')
  pending = writable(false)

  private name = writable('')
  room_info = writable<RoomInfo>([])
  in_room = derived([this.name, this.room_info], ([$name, $room_info]) => {
    return $room_info.some(({ name }) => name === $name)
  })
  game_ongoing = writable(false)
  replay = writable<Replay | null>(null)

  game = new GizmosGame()

  login = (name: string) => {
    this.init_player_socket()
    this.name.set(name)
    this.socket?.emit('login', { name })
  }

  ready = () => {
    this.socket?.emit('ready')
  }

  private step = (action: Action) => {
    this.pending.set(true)
    this.socket?.emit('action', action)
  }

  pick = (energy: Energy) => {
    if (!get(this.game.is_avail)[ActionType.PICK]) return
    this.step({ type: ActionType.PICK, energy })
  }

  file = (id: number) => {
    if (!get(this.game.is_avail)[ActionType.FILE]) return
    this.step({ type: ActionType.FILE, id })
  }

  file_from_research = (id: number) => {
    if (!get(this.game.is_avail)[ActionType.FILE_FROM_RESEARCH]) return
    this.step({ type: ActionType.FILE_FROM_RESEARCH, id })
  }

  build = (
    id: number,
    cost_energy_num: Record<Energy, number>,
    cost_converter_gizmos_id: number[]
  ) => {
    if (!get(this.game.is_avail)[ActionType.BUILD]) return
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
    if (!get(this.game.is_avail)[ActionType.BUILD_FROM_FILED]) return
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
    if (!get(this.game.is_avail)[ActionType.BUILD_FROM_RESEARCH]) return
    this.step({
      type: ActionType.BUILD_FROM_RESEARCH,
      id,
      cost_energy_num,
      cost_converter_gizmos_id,
    })
  }

  research = (level: GizmoLevel) => {
    if (!get(this.game.is_avail)[ActionType.RESEARCH]) return
    this.step({
      type: ActionType.RESEARCH,
      level,
    })
  }

  use_gizmo = (id: number) => {
    if (!get(this.game.is_avail)[ActionType.USE_GIZMO]) return
    this.step({ type: ActionType.USE_GIZMO, id })
  }

  give_up = () => {
    if (!get(this.game.is_avail)[ActionType.GIVE_UP]) return
    this.step({ type: ActionType.GIVE_UP })
  }

  end = () => {
    if (!get(this.game.is_avail)[ActionType.END]) return
    this.step({ type: ActionType.END })
  }

  sample = () => {
    const env = get(this.game.env)
    if (!env) return
    const action = env.sample()
    this.step(action)
    return action
  }

  destroy = () => {
    this.socket?.disconnect()
  }

  init_socket = (socket: Socket) => {
    this.socket = socket
    socket.on('room', (room_info: RoomInfo) => {
      this.room_info.set(room_info)
    })
    socket.on('observation', (observation: Observation) => {
      this.game.on_observation(observation)
      this.pending.set(false)
    })
    socket.on('action', ({ name, action }: ActionLog) => {
      this.game.on_action({ name, action })
    })
    socket.on('start', (player_list: PlayerList) => {
      this.game_ongoing.set(true)
      this.game.player_list.set(player_list)
    })
    socket.on('end', () => {
      this.game_ongoing.set(false)
      this.game.observation.set(null)
      this.game.env.set(null)
    })
    socket.on('replay', replay => {
      this.replay.set(replay)
    })
    socket.on('error', msg => alert(msg))
    socket.on('connect', () => {
      console.log('[socket.connect]')
      this.socket_status.set('green')
    })
    socket.on('disconnect', reason => {
      console.error('[socket.disconnect]', reason)
      this.socket_status.set('red')
    })
    socket.on('connect_error', err => {
      console.error('[socket.connect_error]', err)
      this.socket_status.set('red')
    })
  }

  init_observer_socket = () => {
    this.socket?.disconnect()
    this.init_socket(connect_socket_as_observer())
  }

  init_player_socket = () => {
    this.socket?.disconnect()
    this.init_socket(connect_socket_as_player())
  }

  constructor(socket?: Socket) {
    if (socket) {
      this.init_socket(socket)
    } else {
      this.init_observer_socket()
    }
  }
}
