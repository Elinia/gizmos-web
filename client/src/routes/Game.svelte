<script lang="ts">
  import { readable, type Readable } from 'svelte/store'
  import {
    ALL_ENERGY_TYPES,
    BuildMethod,
    type GizmoLevel,
  } from 'gizmos-env/common'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import type { BuildSolution, PlayerInfo } from 'gizmos-env/Player'
  import Gizmo from './Gizmo.svelte'
  import Energy from './Energy.svelte'
  import Log from './Log.svelte'
  import { render_level } from '$lib/helpers.js'
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

  const LEVELS: GizmoLevel[] = [3, 2, 1]

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

{#if ongoing && $observation && $env && $me}
  {@const my_gizmos = [
    { label: '???Upgrade', gizmos: $me.upgrade_gizmos },
    { label: '???Converter', gizmos: $me.converter_gizmos },
    { label: '????File', gizmos: $me.file_gizmos },
    { label: '????Pick', gizmos: $me.pick_gizmos },
    { label: '????Build', gizmos: $me.build_gizmos },
  ]}
  <div class:pending={$pending}>
    <div>
      <span>Stage: {$observation.curr_stage}</span>
      <span>
        Current player: {$player_list[$observation.curr_player_index].name}
      </span>
    </div>

    <div>Point token: {$me.point_token}</div>
    <div class="flex gap-2">
      <div class="energy">
        Energy ({$me.total_energy_num}/{$me.max_energy_num}):
        <Energy energy_num={$me.energy_num} />
      </div>
    </div>
    <div>
      File ({$me.filed.length}/{$me.max_file_num > 0
        ? $me.max_file_num
        : 'forbidden'}):
      <div class="gizmos">
        {#each $me.filed as g}
          {@const gizmo = $env.gizmo(g.id)}
          {@const solutions = $is_avail[ActionType.BUILD_FROM_FILED]
            ? $env.build_solutions(gizmo, BuildMethod.FROM_FILED)
            : []}
          {@const can_build = solutions.length > 0}
          <div>
            <Gizmo info={gizmo} />
            <button
              class:avail={can_build}
              disabled={!can_build}
              on:click={() => {
                build_dialog = {
                  id: gizmo.id,
                  method: BuildMethod.FROM_FILED,
                  solutions,
                }
                if (build_dialog_element.open) return
                build_dialog_element.showModal()
              }}
            >
              ????
            </button>
          </div>
        {/each}
      </div>
    </div>
    <div>
      Gizmos ({$me.gizmos.length}/{$env.max_gizmos_num} Level3 {$me
        .level3_gizmos.length}/{$env.max_level3_gizmos_num}) :
      {#each my_gizmos as { label, gizmos }}
        <div>{label}:</div>
        <div class="gizmos-simple">
          {#each gizmos as gizmo}
            {@const can_use = $is_avail[ActionType.USE_GIZMO] && gizmo.active}
            <button
              class:avail={can_use}
              disabled={!can_use}
              on:click={() => use_gizmo(gizmo.id)}
            >
              <Gizmo info={gizmo} />
            </button>
          {/each}
        </div>
      {/each}
    </div>
    <div>
      <button
        class:avail={$is_avail[ActionType.GIVE_UP]}
        disabled={!$is_avail[ActionType.GIVE_UP]}
        on:click={() => give_up()}
      >
        Give up
      </button>
      <button
        class:avail={$is_avail[ActionType.END]}
        disabled={!$is_avail[ActionType.END]}
        on:click={() => end()}
      >
        End turn
      </button>
    </div>
    Board:
    <div class="m-10 flex flex-col gap-2 items-center">
      <div class:avail={$is_avail[ActionType.PICK]}>
        Pick energy:
        <div class="energy">
          {#each $observation.energy_board as energy}
            <button
              class={`w-5 h-5 rounded-full ${energy}`}
              on:click={() => pick(energy)}
            />
          {/each}
        </div>
        <div class="text-xs">
          remain: {$observation.energy_pool_num}
        </div>
      </div>
      {#each LEVELS as level}
        <div class="gizmos justify-center">
          <button
            class="w-36"
            class:avail={$is_avail[ActionType.RESEARCH]}
            disabled={!$is_avail[ActionType.RESEARCH]}
            on:click={() => research(level)}
          >
            <div>{render_level(level)}</div>
            <div>????: {$me.research_num}</div>
            <div class="text-xs">
              remain: {$observation.gizmos_pool_num[level]}
            </div>
          </button>
          {#each $observation.gizmos_board[level] as gizmo}
            {@const solutions = $is_avail[ActionType.BUILD]
              ? $env.build_solutions(gizmo.id, BuildMethod.DIRECTLY)
              : []}
            {@const can_build = solutions.length > 0}
            <div>
              <Gizmo info={gizmo} />
              <button
                class:avail={can_build}
                disabled={!can_build}
                on:click={() => {
                  build_dialog = {
                    id: gizmo.id,
                    method: BuildMethod.DIRECTLY,
                    solutions,
                  }
                  if (build_dialog_element.open) return
                  build_dialog_element.showModal()
                }}
              >
                ????
              </button>
              <button
                class:avail={$is_avail[ActionType.FILE]}
                disabled={!$is_avail[ActionType.FILE]}
                on:click={() => file(gizmo.id)}
              >
                ????
              </button>
            </div>
          {/each}
        </div>
      {/each}
    </div>
    Players:
    {#each $observation.players as player, i}
      <div class="font-bold text-lg">
        {$player_list[i].name}
      </div>
      <div>
        ???:{player.point_token} ????:{player.total_energy_num}/{player.max_energy_num}
        ????:{player.filed.length}/{player.max_file_num} ????:{player.research_num}
      </div>
      <div>Estimated score: {player.score}</div>
      <div class="energy">
        <div>Energy:</div>
        <Energy energy_num={player.energy_num} />
      </div>
      <div>
        Gizmos ({player.gizmos.length}/{$env.max_gizmos_num} Level3 {player
          .level3_gizmos.length}/{$env.max_level3_gizmos_num}):
      </div>
      <div class="gizmos-simple">
        {#each player.gizmos as gizmo}
          <Gizmo info={gizmo} simple={true} />
        {/each}
      </div>
      <div>
        File ({player.filed.length}/{player.max_file_num}):
      </div>
      <div class="gizmos-simple">
        {#each player.filed as gizmo}
          <Gizmo info={gizmo} />
        {/each}
      </div>
    {/each}
    <dialog bind:this={build_dialog_element}>
      <form method="dialog">
        {#if build_dialog}
          <div class="flex flex-col gap-2">
            {#each build_dialog.solutions as solution, i}
              <button class="avail" on:click={() => on_build($me, solution)}>
                Solution {i}:
                <div class="energy">
                  Used energy:
                  {#each ALL_ENERGY_TYPES as energy}
                    <span>{energy}: {solution.energy_num[energy]}</span>
                  {/each}
                </div>
                <div class="gizmos-simple">
                  Used gizmos:
                  {#each solution.gizmos as gizmo}
                    <Gizmo info={gizmo} simple={true} />
                  {/each}
                </div>
              </button>
            {/each}
          </div>
        {/if}
        <button value="cancel">Cancel</button>
      </form>
    </dialog>
    <dialog bind:this={research_dialog_element}>
      <form method="dialog">
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
                  on:click={() => {
                    build_dialog = {
                      id: gizmo.id,
                      method: BuildMethod.FROM_RESEARCH,
                      solutions,
                    }
                    build_dialog_element.showModal()
                  }}
                >
                  ????
                </button>
                <button
                  class:avail={can_file}
                  disabled={!can_file}
                  on:click={() => file_from_research(gizmo.id)}
                >
                  ????
                </button>
              </div>
            {/each}
          </div>
        {/if}
        {#if $is_avail[ActionType.GIVE_UP]}
          <button class="avail" value="cancel" on:click={() => give_up()}>
            Give up research
          </button>
        {/if}
      </form>
    </dialog>
  </div>
{/if}
<Log log={$log} />

<style lang="postcss">
  .energy,
  .gizmos,
  .gizmos-simple {
    @apply flex gap-2 flex-wrap;
  }
  .gizmos {
    @apply h-[72px];
  }

  .gizmo {
    @apply border-2 border-black;
  }
  .avail {
    @apply outline outline-2 outline-red-500/50 -outline-offset-1;
  }
  .log {
    @apply resize-y h-80 m-2 p-2 overflow-auto bg-lime-100;
  }

  .pending .avail {
    @apply pointer-events-none outline-none;
  }
</style>
