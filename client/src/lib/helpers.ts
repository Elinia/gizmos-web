import { io } from 'socket.io-client'
import type { AllGizmoLevel } from 'gizmos-env/common'
import { PUBLIC_SERVER_HOST, PUBLIC_SERVER_PORT } from '$env/static/public'

export function render_level(level: AllGizmoLevel) {
  return new Array(level).fill('I').join('')
}

export function connect_socket_as_player() {
  return io(`ws://${PUBLIC_SERVER_HOST}:${PUBLIC_SERVER_PORT}/player`)
}

export function connect_socket_as_observer() {
  return io(`ws://${PUBLIC_SERVER_HOST}:${PUBLIC_SERVER_PORT}/observer`)
}
