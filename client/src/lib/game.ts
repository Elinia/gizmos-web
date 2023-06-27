import { Stage } from 'gizmos-env/common'
import { ActionType, GizmosEnv, type Observation } from 'gizmos-env/GizmosEnv'
import type { PlayerInfo } from 'gizmos-env/Player'
import { derived, get, writable } from 'svelte/store'
import type { ActionLog, LogEntry, PlayerList } from './types.js'

export class GizmosGame {
  player_list = writable<PlayerList>([])
  player_index = derived(
    this.player_list,
    player_list => player_list.find(p => p.me)?.index
  )

  log = writable<LogEntry[]>([])

  observation = writable<Omit<Observation, 'gizmos'> | null>(null)
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

  on_observation = (observation: Omit<Observation, 'gizmos'>) => {
    this.observation.update(prev => {
      if (!prev || observation.curr_turn > prev.curr_turn) {
        this.log.update(log => {
          log.push({ type: 'turn', turn: observation.curr_turn })
          return log
        })
      }
      return observation
    })
    const player_list = get(this.player_list)
    const new_env = new GizmosEnv({
      player_num: player_list.length,
    })
    new_env.simulation(observation)
    this.env.set(new_env)
    if (observation.curr_stage === Stage.GAME_OVER) {
      if (observation.truncated) {
        alert('internal error')
        return
      }
      this.log.update(log => {
        log.push({ type: 'msg', msg: 'GAME OVER!' })
        log.push({ type: 'msg', msg: 'Score:' })
        observation.players.forEach((p, i) =>
          log.push({ type: 'msg', msg: `${player_list[i].name}: ${p.score}` })
        )
        return log
      })
    }
  }

  on_action = ({ name, action }: ActionLog) => {
    this.log.update(log => {
      log.push({ type: 'act', name, action })
      return log
    })
  }
}
