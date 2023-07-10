<script lang="ts">
  import { _ } from 'svelte-i18n'
  import { BuildMethod } from 'gizmos-env/common'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import type { BuildSolution } from 'gizmos-env/Player'
  import type { GizmosGame } from '$lib/game.js'
  import type { GizmosClient } from '$lib/client.js'
  import Gizmo from './Gizmo.svelte'
  import PlayerState from './PlayerState.svelte'

  export let game: GizmosGame

  export let use_gizmo: GizmosClient['use_gizmo']
  export let give_up: GizmosClient['give_up']
  export let end: GizmosClient['end']

  export let show_build_dialog: (
    id: number,
    method: BuildMethod,
    solutions: BuildSolution[]
  ) => void

  const { me, env, is_avail } = game
</script>

{#if $env && $me}
  {@const my_gizmos = [
    { label: $_('upgrade'), gizmos: $me.upgrade_gizmos },
    { label: $_('converter'), gizmos: $me.converter_gizmos },
    { label: $_('file'), gizmos: $me.file_gizmos },
    { label: $_('pick'), gizmos: $me.pick_gizmos },
    { label: $_('build'), gizmos: $me.build_gizmos },
  ]}
  <PlayerState env={$env} player={$me} />
  <div class="flex gap-2">
    <div class="flex flex-col gap-2 border-2 border-blue-300 p-2 rounded-md">
      <div>
        📁 ({$me.filed.length}/{$me.max_file_num > 0
          ? $me.max_file_num
          : 'forbidden'})
      </div>
      <div class="flex flex-col gap-2">
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
              on:click={() =>
                show_build_dialog(gizmo.id, BuildMethod.FROM_FILED, solutions)}
            >
              🔧
            </button>
          </div>
        {/each}
      </div>
    </div>
    <div class="grid grid-cols-5 gap-2 border-2 border-blue-300 p-2 rounded-md">
      {#each my_gizmos as { label, gizmos }}
        <div class="flex flex-col gap-2">
          <div>{label}</div>
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
  </div>
  <div>
    <button
      class:avail={$is_avail[ActionType.GIVE_UP]}
      disabled={!$is_avail[ActionType.GIVE_UP]}
      on:click={() => give_up()}
    >
      {$_('give_up')}
    </button>
    <button
      class:avail={$is_avail[ActionType.END]}
      disabled={!$is_avail[ActionType.END]}
      on:click={() => end()}
    >
      {$_('end_turn')}
    </button>
  </div>
{/if}
