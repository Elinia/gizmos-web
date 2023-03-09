<script lang="ts">
  import type { Observation } from 'gizmos-env/GizmosEnv'
  import { GizmosGame } from '$lib/game.js'
  import type { ActionLog, Replay } from '$lib/types.js'
  import Game from '../Game.svelte'

  export let replay: Replay

  const game = new GizmosGame()
  let step = 0

  const { observation, on_observation, on_action, log, player_list } = game

  function is_action(r: any): r is ActionLog {
    return 'action' in r
  }

  function is_observation(r: any): r is Omit<Observation, 'gizmos'> {
    return 'curr_stage' in r
  }

  function on_step(step: number) {
    observation.set(null)
    log.set([])
    for (let i = 0; i <= step; i++) {
      const r = replay[i]
      if (is_action(r)) {
        // action
        if (!$observation) return
        on_action(r)
      } else if (is_observation(r)) {
        // observation
        player_list.set(
          r.players!.map((_, j) => ({
            name: `Player${j}`,
            index: j,
            me: r.curr_player_index === j,
          }))
        )
        on_observation(r)
      }
    }
  }

  $: {
    on_step(step)
  }
</script>

<input
  type="range"
  min={0}
  max={replay.length - 1}
  step={1}
  bind:value={step}
/>
{step}
<Game {game} />

<svelte:window
  on:keydown|preventDefault={e => {
    switch (e.key) {
      case 'ArrowRight':
        if (step + 1 < replay.length) step += 1
        return
      case 'ArrowLeft':
        if (step - 1 >= 0) step -= 1
        return
    }
  }}
/>
