<script lang="ts">
  import { flip } from 'svelte/animate'
  import { _ } from 'svelte-i18n'
  import { BuildMethod, type GizmoLevel } from 'gizmos-env/common'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import type { BuildSolution } from 'gizmos-env/Player'
  import Gizmo from './Gizmo.svelte'
  import { render_level } from '$lib/helpers.js'
  import type { GizmosClient } from '$lib/client.js'
  import type { GizmosGame } from '$lib/game.js'
  import { send } from '$lib/transition.js'

  export let game: GizmosGame

  export let pick: GizmosClient['pick']
  export let file: GizmosClient['file']
  export let research: GizmosClient['research']

  export let show_build_dialog: (
    id: number,
    method: BuildMethod,
    solutions: BuildSolution[]
  ) => void

  const LEVELS: GizmoLevel[] = [3, 2, 1]
  const { observation, me, env, is_avail } = game
</script>

{#if $env && $observation}
  <div class="flex flex-col gap-2 items-center">
    <div class:avail={$is_avail[ActionType.PICK]}>
      {$_('energy_row')}:
      <div class="energy">
        {#each $observation.energy_board as energy}
          <button
            class={`w-5 h-5 rounded-full ${energy}`}
            on:click={() => pick(energy)}
          />
        {/each}
      </div>
      <div class="text-xs">
        {$_('remain')}: {$observation.energy_pool_num}
      </div>
    </div>
    <div class="display-area">
      {#each LEVELS as level}
        <div class="gizmos justify-center">
          <button
            class="w-36"
            class:avail={$is_avail[ActionType.RESEARCH]}
            disabled={!$is_avail[ActionType.RESEARCH]}
            on:click={() => research(level)}
          >
            <div class="font-bold">{render_level(level)}</div>
            {#if $me}
              <div>🔍×{$me.research_num}</div>
            {/if}
            <div class="text-xs">
              {$_('remain')}: {$observation.gizmos_pool_num[level]}
            </div>
          </button>
          {#each $observation.gizmos_board[level] as gizmo (gizmo.id)}
            {@const solutions = $is_avail[ActionType.BUILD]
              ? $env.build_solutions(gizmo.id, BuildMethod.DIRECTLY)
              : []}
            {@const can_build = solutions.length > 0}
            <div animate:flip={{ duration: 200 }} out:send={{ key: gizmo.id }}>
              <Gizmo info={gizmo} />
              <button
                class:avail={can_build}
                disabled={!can_build}
                on:click={() =>
                  show_build_dialog(gizmo.id, BuildMethod.DIRECTLY, solutions)}
              >
                🔧
              </button>
              <button
                class:avail={$is_avail[ActionType.FILE]}
                disabled={!$is_avail[ActionType.FILE]}
                on:click={() => file(gizmo.id)}
              >
                📁
              </button>
            </div>
          {/each}
        </div>
      {/each}
    </div>
  </div>
{/if}

<style lang="postcss">
  .display-area {
    @apply flex flex-col gap-2 items-center;

    :global(.sm) & {
      @apply flex-row-reverse items-start;
      .gizmos {
        @apply h-auto flex-1;
      }
    }
  }
</style>
