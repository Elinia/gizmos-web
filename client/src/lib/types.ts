import type { Observation, Action } from 'gizmos-env/GizmosEnv'

export type PlayerList = {
  name: string
  index: number
  me: boolean
}[]

export type ActionLog = { name: string; action: Action }

export type Replay = (Omit<Observation, 'gizmos'> | ActionLog)[]
