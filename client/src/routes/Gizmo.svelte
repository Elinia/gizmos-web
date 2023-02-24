<script lang="ts">
  import { BuildMethod } from 'gizmos-env/common'
  import { gizmos } from 'gizmos-env/gizmos_pool'
  import {
    is_build_gizmo,
    is_converter_gizmo,
    is_file_gizmo,
    is_pick_gizmo,
    is_upgrade_gizmo,
    type GizmoInfo,
  } from 'gizmos-env/Gizmo'
  import { render_level } from '$lib/helpers.js'
  import Effect from './Effect.svelte'

  export let info: GizmoInfo
  export let simple: boolean = false
  export let stateless: boolean = false
  $: active = info.active
  $: used = info.used
  $: gizmo = gizmos[info.id]
</script>

<div class="gizmo" class:simple class:active class:used class:stateless>
  {#if !simple}
    <div class={`text-white text-center ${gizmo.energy_type}`}>
      <span>💰:{gizmo.energy_cost}</span>
      <span>⭐:{gizmo.value || 'X'}</span>
    </div>
  {/if}
  <div class="flex place-content-center place-items-center">
    {#if is_build_gizmo(gizmo)}
      <div class="flex">
        <span>🔧</span>
        <span>
          {#if gizmo.when_build.method !== 'any'}
            {#each gizmo.when_build.method as method}
              <div class="w-3 h-3 text-2xs">
                {method === BuildMethod.FROM_FILED
                  ? '📁'
                  : method === BuildMethod.FROM_RESEARCH
                  ? '🔍'
                  : ''}
              </div>
            {/each}
          {/if}
        </span>
        <span>
          {#if gizmo.when_build.level !== 'any'}
            {#each gizmo.when_build.level as level}
              <div class="w-3 h-3 text-2xs font-serif">
                {render_level(level)}
              </div>
            {/each}
          {/if}
        </span>
        <span>
          {#if gizmo.when_build.energy !== 'any'}
            {#each gizmo.when_build.energy as energy}
              <div class={`w-2.5 h-2.5 rounded-full ${energy}`} />
            {/each}
          {/if}
        </span>
      </div>
      <span>👉</span>
    {:else if is_converter_gizmo(gizmo)}
      {#if gizmo.prerequisite}
        {#each gizmo.prerequisite.level as level}
          <span class="font-serif">
            {render_level(level)}:💰-1
          </span>
        {/each}
      {:else}
        {#each gizmo.formulae as formula, i}
          {#if i > 0}
            <span class="w-0.5 h-5 ml-2 mr-2 bg-gray-600" />
          {/if}
          {#each new Array(formula.from.num).fill(formula.from.energy) as energy}
            <span class={`w-4 h-4 rounded-full ${energy}`} />
          {/each}
          <span class="ml-0.5 mr-0.5">→</span>
          {#each new Array(formula.to.num).fill(formula.to.energy) as energy}
            <span class={`w-4 h-4 rounded-full ${energy}`} />
          {/each}
        {/each}
      {/if}
    {:else if is_upgrade_gizmo(gizmo)}
      <span class="mr-2">➕</span>
      <div>
        {#if gizmo.max_energy_num > 0}
          <span>🔮{gizmo.max_energy_num}</span>
        {/if}
        {#if gizmo.max_file_num > 0}
          <span>📁{gizmo.max_file_num}</span>
        {/if}
        {#if gizmo.research_num > 0}
          <span>🔍{gizmo.research_num}</span>
        {/if}
        {#if gizmo.build_from_filed_cost_reduction > 0}
          <div class="flex">
            <span>🔧</span>
            <span class="w-3 h-3 text-2xs">📁</span>
            <span>-{gizmo.build_from_filed_cost_reduction}</span>
          </div>
        {/if}
        {#if gizmo.build_from_research_cost_reduction > 0}
          <div class="flex">
            <span>🔧</span>
            <span class="w-3 h-3 text-2xs">🔍</span>
            <span>-{gizmo.build_from_research_cost_reduction}</span>
          </div>
        {/if}
        {#if gizmo.max_file_num < 0}
          <div>🚫📁</div>
        {/if}
        {#if gizmo.research_num < 0}
          <div>🚫🔍</div>
        {/if}
      </div>
    {:else if is_pick_gizmo(gizmo)}
      <div class="flex">
        <span>👌</span>
        <span>
          {#each gizmo.when_pick as energy}
            <div class={`w-2.5 h-2.5 rounded-full ${energy}`} />
          {/each}
        </span>
      </div>
      <span>👉</span>
    {:else if is_file_gizmo(gizmo)}
      <span>📁</span>
      <span>👉</span>
    {/if}
    {#if gizmo.effect.type !== 'na'}
      <Effect effect={gizmo.effect} />
    {/if}
  </div>
</div>

<style lang="postcss">
  .gizmo {
    @apply w-36 bg-lime-100;
  }
  .active:not(.stateless) {
    @apply brightness-110;
  }
  .used:not(.stateless) {
    @apply brightness-75;
  }
</style>
