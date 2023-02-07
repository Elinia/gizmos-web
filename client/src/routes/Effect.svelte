<script lang="ts">
  import type { Effect } from 'gizmos-env/Gizmo'
  import { render_level } from '$lib/helpers.js'

  export let effect: Effect
</script>

<span class="flex">
  {#if effect.type === 'add_point_token'}
    {new Array(effect.num).fill('⭐').join('')}
  {/if}
  {#if effect.type === 'draw_from_pool'}
    {new Array(effect.num).fill('🙈').join('')}
  {/if}
  {#if effect.type === 'energy_as_point'}
    X=🔮
  {/if}
  {#if effect.type === 'extra_build'}
    {#each effect.level as level}
      🔧
      <span class="w-3 h-3 text-2xs font-serif">
        {render_level(level)}
      </span>
    {/each}
  {/if}
  {#if effect.type === 'extra_file'}
    📁
  {/if}
  {#if effect.type === 'extra_research'}
    🔍
  {/if}
  {#if effect.type === 'free_pick'}
    {new Array(effect.num).fill('👌').join('')}
  {/if}
  {#if effect.type === 'token_as_point'}
    X=⭐
  {/if}
</span>
