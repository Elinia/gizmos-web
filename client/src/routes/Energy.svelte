<script lang="ts">
  import { ALL_ENERGY_TYPES, type Energy } from 'gizmos-env/common'

  export let energy_num: Record<Energy, number>
</script>

{#each ALL_ENERGY_TYPES as energy}
  {@const num = energy_num[energy]}
  {#each new Array(num).fill(energy) as e}
    <div class={`w-5 h-5 rounded-full ${e}`} />
  {/each}
{/each}
