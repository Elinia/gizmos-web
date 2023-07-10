import type { Observation, Action } from 'gizmos-env/GizmosEnv'

export type PlayerList = {
  name: string
  index: number
  me: boolean
}[]

export type ActionLog = { name: string; action: Action }

type MsgLogEntry = { type: 'msg'; msg: string }
type ActionLogEntry = { type: 'act'; name: string; action: Action }
type TurnLogEntry = { type: 'turn'; turn: number }
type ResultLogEntry = {
  type: 'result'
  result: { name: string; score: string; me: boolean }[]
}
export type LogEntry =
  | MsgLogEntry
  | ActionLogEntry
  | TurnLogEntry
  | ResultLogEntry

export type Replay = (Omit<Observation, 'gizmos'> | ActionLog)[]
