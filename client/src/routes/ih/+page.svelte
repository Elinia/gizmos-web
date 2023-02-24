<script lang="ts">
  import { gizmos } from 'gizmos-env/gizmos_pool'
  import Gizmo from '../Gizmo.svelte'
</script>

{#each gizmos as gizmo}
  <span>{gizmo.id}</span>
  <Gizmo stateless={true} info={gizmo.info} />
{/each}
