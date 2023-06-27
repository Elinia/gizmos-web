<script lang="ts">
  import { BuildMethod, type GizmoLevel } from 'gizmos-env/common'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import type { BuildSolution, PlayerInfo } from 'gizmos-env/Player'
  import type { GizmosGame } from '$lib/game.js'
  import type { GizmosClient } from '$lib/client.js'
  import Gizmo from './Gizmo.svelte'
  import Energy from './Energy.svelte'

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
    { label: '➕Upgrade', gizmos: $me.upgrade_gizmos },
    { label: '→Converter', gizmos: $me.converter_gizmos },
    { label: '📁File', gizmos: $me.file_gizmos },
    { label: '👌Pick', gizmos: $me.pick_gizmos },
    { label: '🔧Build', gizmos: $me.build_gizmos },
  ]}
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
            on:click={() =>
              show_build_dialog(gizmo.id, BuildMethod.FROM_FILED, solutions)}
          >
            🔧
          </button>
        </div>
      {/each}
    </div>
  </div>
  <div>
    Gizmos ({$me.gizmos.length}/{$env.max_gizmos_num} Level3 {$me.level3_gizmos
      .length}/{$env.max_level3_gizmos_num}) :
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
{/if}
