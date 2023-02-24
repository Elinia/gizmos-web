<script lang="ts">
  import { BuildMethod, type AllGizmoLevel } from 'gizmos-env/common'
  import {
    type Gizmo,
    is_build_gizmo_info,
    is_converter_gizmo_info,
    is_file_gizmo_info,
    is_pick_gizmo_info,
    is_upgrade_gizmo_info,
  } from 'gizmos-env/Gizmo'
  import { render_level } from '$lib/helpers.js'
  import Effect from './Effect.svelte'

  export let info: Gizmo<AllGizmoLevel>['info']
  export let simple: boolean = false
  export let stateless: boolean = false
  $: active = info.active
  $: used = info.used
</script>

<div class="gizmo" class:simple class:active class:used class:stateless>
  {#if !simple}
    <div class={`text-white text-center ${info.energy_type}`}>
      <span>💰:{info.energy_cost}</span>
      <span>⭐:{info.value || 'X'}</span>
    </div>
  {/if}
  <div class="flex place-content-center place-items-center">
    {#if is_build_gizmo_info(info)}
      <div class="flex">
        <span>🔧</span>
        <span>
          {#if info.when_build.method !== 'any'}
            {#each info.when_build.method as method}
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
          {#if info.when_build.level !== 'any'}
            {#each info.when_build.level as level}
              <div class="w-3 h-3 text-2xs font-serif">
                {render_level(level)}
              </div>
            {/each}
          {/if}
        </span>
        <span>
          {#if info.when_build.energy !== 'any'}
            {#each info.when_build.energy as energy}
              <div class={`w-2.5 h-2.5 rounded-full ${energy}`} />
            {/each}
          {/if}
        </span>
      </div>
      <span>👉</span>
    {:else if is_converter_gizmo_info(info)}
      {#if info.prerequisite}
        {#each info.prerequisite.level as level}
          <span class="font-serif">
            {render_level(level)}:💰-1
          </span>
        {/each}
      {:else}
        {#each info.formulae as formula, i}
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
    {:else if is_upgrade_gizmo_info(info)}
      <span class="mr-2">➕</span>
      <div>
        {#if info.max_energy_num > 0}
          <span>🔮{info.max_energy_num}</span>
        {/if}
        {#if info.max_file_num > 0}
          <span>📁{info.max_file_num}</span>
        {/if}
        {#if info.research_num > 0}
          <span>🔍{info.research_num}</span>
        {/if}
        {#if info.build_from_filed_cost_reduction > 0}
          <div class="flex">
            <span>🔧</span>
            <span class="w-3 h-3 text-2xs">📁</span>
            <span>-{info.build_from_filed_cost_reduction}</span>
          </div>
        {/if}
        {#if info.build_from_research_cost_reduction > 0}
          <div class="flex">
            <span>🔧</span>
            <span class="w-3 h-3 text-2xs">🔍</span>
            <span>-{info.build_from_research_cost_reduction}</span>
          </div>
        {/if}
        {#if info.max_file_num < 0}
          <div>🚫📁</div>
        {/if}
        {#if info.research_num < 0}
          <div>🚫🔍</div>
        {/if}
      </div>
    {:else if is_pick_gizmo_info(info)}
      <div class="flex">
        <span>👌</span>
        <span>
          {#each info.when_pick as energy}
            <div class={`w-2.5 h-2.5 rounded-full ${energy}`} />
          {/each}
        </span>
      </div>
      <span>👉</span>
    {:else if is_file_gizmo_info(info)}
      <span>📁</span>
      <span>👉</span>
    {/if}
    {#if info.effect.type !== 'na'}
      <Effect effect={info.effect} />
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
