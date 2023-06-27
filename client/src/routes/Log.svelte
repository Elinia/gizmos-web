<script lang="ts">
  import { render_level } from '$lib/helpers.js'
  import type { LogEntry } from '$lib/types.js'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import { gizmos } from 'gizmos-env/gizmos_pool'
  import Energy from './Energy.svelte'
  import Gizmo from './Gizmo.svelte'

  export let log: LogEntry[]
</script>

<div class="log">
  {#each log as logEntry}
    {#if logEntry.type === 'msg'}
      <div>{logEntry.msg}</div>
    {:else if logEntry.type === 'turn'}
      <div class="bg-green-200 -mx-2 text-center">Turn {logEntry.turn}</div>
    {:else}
      {@const action = logEntry.action}
      <div class="flex flex-wrap items-center gap-2">
        <span>{logEntry.name}:</span>
        {#if action.type === ActionType.PICK}
          <div>👌</div>
          <div class={`w-5 h-5 rounded-full ${action.energy}`} />
        {:else if action.type === ActionType.FILE || action.type === ActionType.FILE_FROM_RESEARCH}
          <div>📁</div>
          <Gizmo stateless={true} info={gizmos[action.id].info} />
        {:else if action.type === ActionType.BUILD}
          <div>🔧</div>
          <Gizmo stateless={true} info={gizmos[action.id].info} />
          <Energy energy_num={action.cost_energy_num} />
          {#if action.cost_converter_gizmos_id.length > 0}
            <div>➕</div>
          {/if}
          {#each action.cost_converter_gizmos_id as id}
            <Gizmo stateless={true} simple={true} info={gizmos[id].info} />
          {/each}
        {:else if action.type === ActionType.BUILD_FROM_FILED}
          <div class="flex">
            <span>🔧</span>
            <span>
              <div class="w-3 h-3 text-2xs">📁</div>
            </span>
          </div>
          <Gizmo stateless={true} info={gizmos[action.id].info} />
          <Energy energy_num={action.cost_energy_num} />
          {#if action.cost_converter_gizmos_id.length > 0}
            <div>➕</div>
          {/if}
          {#each action.cost_converter_gizmos_id as id}
            <Gizmo stateless={true} simple={true} info={gizmos[id].info} />
          {/each}
        {:else if action.type === ActionType.BUILD_FROM_RESEARCH}
          <div class="flex">
            <span>🔧</span>
            <span>
              <div class="w-3 h-3 text-2xs">🔍</div>
            </span>
          </div>
          <Gizmo stateless={true} info={gizmos[action.id].info} />
          <Energy energy_num={action.cost_energy_num} />
          {#if action.cost_converter_gizmos_id.length > 0}
            <div>➕</div>
          {/if}
          {#each action.cost_converter_gizmos_id as id}
            <Gizmo stateless={true} simple={true} info={gizmos[id].info} />
          {/each}
        {:else if action.type === ActionType.BUILD_FOR_FREE}
          <div>🔧</div>
          <Gizmo stateless={true} info={gizmos[action.id].info} />
        {:else if action.type === ActionType.RESEARCH}
          <div>🔍</div>
          <div class="font-serif">
            {render_level(action.level)}
          </div>
        {:else if action.type === ActionType.USE_GIZMO}
          <div>✨</div>
          <Gizmo stateless={true} info={gizmos[action.id].info} />
        {:else if action.type === ActionType.GIVE_UP}
          <div>🙅‍♀️</div>
        {:else if action.type === ActionType.END}
          <div>🔚</div>
        {:else}
          <div />
        {/if}
      </div>
    {/if}
  {/each}
</div>

<style lang="postcss">
  .log {
    @apply resize-y h-80 p-2 overflow-auto bg-blue-200 flex flex-col gap-1;
  }
</style>
