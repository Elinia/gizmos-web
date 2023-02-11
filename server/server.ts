import { Server, Socket } from 'socket.io'
import { Stage } from 'gizmos-env/common'
import { GizmosEnv, type Action } from 'gizmos-env/GizmosEnv'
import { shuffle } from 'gizmos-env/utils'
import { PORT } from './config.js'

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

function broadcastObservation() {
  const env = getEnv()
  playersSocketID.forEach((id, i) => {
    const info = getPlayerInfo(id)
    info.socket.emit('observation', env.observation(i))
  })
}

function broadcastRoom() {
  const roomInfo: { name: string; ready: boolean }[] = []
  playersInfo.forEach(({ name, ready }) => roomInfo.push({ name, ready }))
  io.of('/player').emit('room', roomInfo)
}

function startGame() {
  globalEnv = new GizmosEnv(playersInfo.size)
  globalEnv.reset()
  playersSocketID = shuffle(Array.from(playersInfo).map(([id]) => id))
  Array.from(playersInfo).forEach(([id]) => {
    const info = getPlayerInfo(id)
    const playerList = playersSocketID.map((_id, i) => {
      const info = getPlayerInfo(_id)
      return {
        name: info.name,
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
  io.of('/player').emit('end')
  broadcastRoom()
}

io.of('/player').on('connection', socket => {
  console.log(`[connect] ${socket.id}`)

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
    playersInfo.delete(socket.id)
    // reconnect mechanism?
    endGame()
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
      playersInfo.size >= 2 &&
      Array.from(playersInfo).every(([, info]) => info.ready)
    ) {
      startGame()
    }
  })

  socket.on('action', (action: Action) => {
    const env = getEnv()
    console.log(`[action]: ${playersSocketID.indexOf(socket.id)}`, action)
    env.step(playersSocketID.indexOf(socket.id), action)
    broadcastObservation()
    if (env.state.curr_stage === Stage.GAME_OVER) {
      endGame()
    }
  })

  socket.on('observation', () => {
    const i = playersSocketID.indexOf(socket.id)
    const env = getEnv()
    socket.emit('observation', env.observation(i))
  })
})
