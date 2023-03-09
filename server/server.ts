import { Server, Socket } from 'socket.io'
import { Stage } from 'gizmos-env/common'
import { GizmosEnv, Observation, type Action } from 'gizmos-env/GizmosEnv'
import { shuffle } from 'gizmos-env/utils'
import { PORT } from './config.js'

function clone<T extends object>(obj: T): T {
  // return structuredClone(obj)
  return JSON.parse(JSON.stringify(obj))
}

const io = new Server(PORT, {
  cors: {
    origin: '*',
  },
})

const playersInfo = new Map<
  Socket['id'],
  { name: string; ready: boolean; socket: Socket }
>()
let playersSocketID: Socket['id'][] = []
let globalEnv: GizmosEnv | null = null
let replay: (Omit<Observation, 'gizmos'> | { name: string; action: Action })[] =
  []

function getPlayerInfo(id: Socket['id']) {
  const info = playersInfo.get(id)
  if (!info) {
    throw new Error(`no player with socket id: ${id}`)
  }
  return info
}

function getEnv() {
  if (!globalEnv) {
    throw new Error('no env')
  }
  return globalEnv
}

function broadcastAction(socket: Socket, action: Action) {
  const info = getPlayerInfo(socket.id)
  io.of('/player').emit('action', { name: info.name, action })
  replay.push({ name: info.name, action })
}

function broadcastObservation() {
  const env = getEnv()
  playersSocketID.forEach((id, i) => {
    const info = getPlayerInfo(id)
    const observation = env.observation(i)
    info.socket.emit('observation', observation)
    if (i === observation.curr_player_index) {
      const { gizmos, ...rob } = observation
      replay.push(clone(rob))
    }
  })
}

function broadcastRoom() {
  const roomInfo: { name: string; ready: boolean }[] = []
  playersInfo.forEach(({ name, ready }) => roomInfo.push({ name, ready }))
  io.of('/player').emit('room', roomInfo)
}

function startGame() {
  replay = []
  globalEnv = new GizmosEnv({ player_num: playersInfo.size })
  playersSocketID = shuffle(Array.from(playersInfo).map(([id]) => id))
  Array.from(playersInfo).forEach(([id]) => {
    const info = getPlayerInfo(id)
    const playerList = playersSocketID.map((_id, i) => {
      const { name } = getPlayerInfo(_id)
      return {
        name,
        index: i,
        me: _id === id,
      }
    })
    info.socket.emit('start', playerList)
  })
  broadcastObservation()
}

function endGame() {
  globalEnv = null
  playersSocketID = []
  Array.from(playersInfo).forEach(([id]) => {
    const info = getPlayerInfo(id)
    playersInfo.set(id, { ...info, ready: false })
  })
  io.of('/player').emit('replay', replay)
  replay = []
  io.of('/player').emit('end')
  broadcastRoom()
}

io.of('/player').on('connection', socket => {
  console.log(`[connect] ${socket.id}`)
  broadcastRoom()

  socket.on('login', ({ name }: { name: string }) => {
    console.log(`[login] ${socket.id} ${name}`)
    if (
      Array.from(playersInfo)
        .map(([, info]) => info.name)
        .includes(name)
    ) {
      socket.emit('error', 'name exists')
      return
    }
    playersInfo.set(socket.id, { socket, name, ready: false })
    broadcastRoom()
  })

  socket.on('disconnect', reason => {
    console.log(`[disconnect] ${socket.id}`)
    if (playersInfo.has(socket.id)) {
      playersInfo.delete(socket.id)
      broadcastRoom()
    }
    // reconnect mechanism?
    if (globalEnv) {
      endGame()
    }
  })

  socket.on('ready', () => {
    console.log(`[ready] ${socket.id}`)
    // game running
    if (globalEnv !== null) {
      return
    }
    const info = getPlayerInfo(socket.id)
    info.ready = !info.ready
    broadcastRoom()
    if (
      playersInfo.size >= 1 &&
      Array.from(playersInfo).every(([, info]) => info.ready)
    ) {
      startGame()
    }
  })

  socket.on('action', (action: Action) => {
    const env = getEnv()
    const playerIndex = playersSocketID.indexOf(socket.id)
    console.log(`[action] ${playerIndex}`, action)
    env.step(playerIndex, action)
    broadcastAction(socket, action)
    broadcastObservation()
    if (env.state.curr_stage === Stage.GAME_OVER) {
      endGame()
    }
  })

  socket.on('observation', () => {
    const env = getEnv()
    const playerIndex = playersSocketID.indexOf(socket.id)
    socket.emit('observation', env.observation(playerIndex))
  })
})
