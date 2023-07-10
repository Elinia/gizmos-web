<script lang="ts">
  import { readable, type Readable } from 'svelte/store'
  import { _ } from 'svelte-i18n'
  import { BuildMethod } from 'gizmos-env/common'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import type { BuildSolution, PlayerInfo } from 'gizmos-env/Player'
  import Me from './Me.svelte'
  import Board from './Board.svelte'
  import Gizmo from './Gizmo.svelte'
  import Energy from './Energy.svelte'
  import Log from './Log.svelte'
  import PlayerState from './PlayerState.svelte'
  import type { GizmosClient } from '$lib/client.js'
  import type { GizmosGame } from '$lib/game.js'

  const noop = () => undefined

  export let ongoing: boolean = true
  export let game: GizmosGame
  export let pending: Readable<boolean> = readable(false)
  export let pick: GizmosClient['pick'] = noop
  export let file: GizmosClient['file'] = noop
  export let file_from_research: GizmosClient['file_from_research'] = noop
  export let build: GizmosClient['build'] = noop
  export let build_from_filed: GizmosClient['build_from_filed'] = noop
  export let build_from_research: GizmosClient['build_from_research'] = noop
  export let research: GizmosClient['research'] = noop
  export let use_gizmo: GizmosClient['use_gizmo'] = noop
  export let give_up: GizmosClient['give_up'] = noop
  export let end: GizmosClient['end'] = noop

  const { log, player_list, me, env, observation, is_avail } = game

  $: console.log($observation)
  $: console.log($env, $env?.action_space)

  let build_dialog_element: HTMLDialogElement
  let build_dialog: {
    id: number
    method: BuildMethod
    solutions: BuildSolution[]
  } | null = null

  function on_build(me: PlayerInfo | null, solution: BuildSolution) {
    if (!me || !build_dialog) return
    const common_params = [
      build_dialog.id,
      solution.energy_num,
      solution.gizmos.map(g => g.id),
    ] as const
    switch (build_dialog.method) {
      case BuildMethod.DIRECTLY:
        build(...common_params)
        break
      case BuildMethod.FROM_FILED:
        build_from_filed(...common_params)
        break
      case BuildMethod.FROM_RESEARCH:
        build_from_research(...common_params)
        break
      default:
        throw new Error('unexpected build method')
    }
  }

  function show_build_dialog(
    id: number,
    method: BuildMethod,
    solutions: BuildSolution[]
  ) {
    build_dialog = {
      id,
      method,
      solutions,
    }
    if (build_dialog_element.open) return
    build_dialog_element.showModal()
  }

  let research_dialog_element: HTMLDialogElement
  $: if (research_dialog_element && $observation?.researching) {
    if (!research_dialog_element.open) {
      research_dialog_element.showModal()
    }
  }
  $: if (research_dialog_element && !$observation?.researching) {
    research_dialog_element.close()
  }

  $: if (build_dialog_element) {
    build_dialog_element.addEventListener('close', () => {
      build_dialog = null
    })
  }
</script>

{#if ongoing && $observation && $env}
  <div class:pending={$pending}>
    <div>
      <span>{$_('stage')}: {$observation.curr_stage}</span>
      <span>
        {$_('curr_player')}: {$player_list[$observation.curr_player_index].name}
      </span>
    </div>

    <div class="game-board">
      <div class="area me">
        <Me {game} {use_gizmo} {give_up} {end} {show_build_dialog} />
      </div>
      <div class="area board">
        <Board {game} {pick} {file} {research} {show_build_dialog} />
      </div>
      <div class="log">
        <Log log={$log} />
      </div>
      <div class="area players">
        {#each $observation.players as player, i}
          <div class="font-bold text-lg">
            {$player_list[i].name}
          </div>
          <PlayerState env={$env} {player} />
          <div class="gizmos-simple">
            {#each player.gizmos as gizmo}
              <Gizmo info={gizmo} simple={true} />
            {/each}
          </div>
          <div>
            📁 ({player.filed.length}/{player.max_file_num}):
          </div>
          <div class="gizmos-simple">
            {#each player.filed as gizmo}
              <Gizmo info={gizmo} />
            {/each}
          </div>
        {/each}
      </div>
    </div>

    <dialog bind:this={build_dialog_element}>
      <form method="dialog" class="flex flex-col gap-2 min-w-[10em]">
        <div class="dialog-title">{$_('build')}</div>
        {#if build_dialog}
          <div class="flex flex-col gap-2">
            {#each build_dialog.solutions as solution, i}
              <button class="avail" on:click={() => on_build($me, solution)}>
                {$_('solution')}
                {i}:
                <div class="energy">
                  {$_('spend')}:
                  <Energy energy_num={solution.energy_num} />
                </div>
                {#if solution.gizmos.length > 0}
                  <div class="gizmos-simple">
                    {$_('use')}:
                    {#each solution.gizmos as gizmo}
                      <Gizmo info={gizmo} simple={true} />
                    {/each}
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        {/if}
        <button
          value="cancel"
          on:click={() => {
            if ($observation?.researching) {
              research_dialog_element.showModal()
            }
          }}
        >
          {$_('cancel')}
        </button>
      </form>
    </dialog>
    <dialog bind:this={research_dialog_element}>
      <form method="dialog" class="flex flex-col gap-2">
        <div class="dialog-title">{$_('research')}</div>
        {#if $observation.researching}
          <div class="gizmos">
            {#each $observation.researching.gizmos as g}
              {@const gizmo = $env.gizmo(g.id)}
              {@const solutions = $is_avail[ActionType.BUILD_FROM_RESEARCH]
                ? $env.build_solutions(gizmo, BuildMethod.FROM_RESEARCH)
                : []}
              {@const can_build = solutions.length > 0}
              {@const can_file = $is_avail[ActionType.FILE_FROM_RESEARCH]}
              <div>
                <Gizmo info={gizmo} />
                <button
                  class:avail={can_build}
                  disabled={!can_build}
                  on:click={() =>
                    show_build_dialog(
                      gizmo.id,
                      BuildMethod.FROM_RESEARCH,
                      solutions
                    )}
                >
                  🔧
                </button>
                <button
                  class:avail={can_file}
                  disabled={!can_file}
                  on:click={() => file_from_research(gizmo.id)}
                >
                  📁
                </button>
              </div>
            {/each}
          </div>
        {/if}
        {#if $is_avail[ActionType.GIVE_UP]}
          <button class="avail" value="cancel" on:click={() => give_up()}>
            {$_('give_up')}
          </button>
        {/if}
      </form>
    </dialog>
  </div>
{/if}
{#if !ongoing}
  <Log log={$log} />
{/if}

<style lang="postcss">
  .game-board {
    @apply grid gap-4 p-4;
    grid-template-columns: 48em minmax(0, 1fr);
    grid-template-rows: auto auto auto;
    grid-template-areas:
      'me me'
      'board log'
      'players players';
  }

  .area {
    @apply rounded-md bg-blue-200 p-2 flex flex-col gap-2;
  }

  .me {
    grid-area: me;
  }

  .board {
    grid-area: board;
  }

  .log {
    grid-area: log;
  }

  .players {
    grid-area: players;
  }

  .dialog-title {
    @apply text-lg text-center font-bold;
  }

  .pending .avail {
    @apply pointer-events-none outline-none;
  }
</style>
