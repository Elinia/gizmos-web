<script lang="ts">
  import type { Observation, Action } from 'gizmos-env/GizmosEnv'
  import Replay from './Replay.svelte'
  let replay: (Observation | { name: string; action: Action })[] = []
</script>

<div>
  <input
    type="file"
    accept=".json"
    on:change={e => {
      if (!e.currentTarget.files) return
      const file = e.currentTarget.files[0]
      if (file.type !== 'application/json') return
      const reader = new FileReader()
      reader.addEventListener('load', ee => {
        const text = ee.target?.result
        if (!text || text instanceof ArrayBuffer) return
        replay = JSON.parse(text)
      })
      reader.readAsText(file)
    }}
  />
</div>
{#if replay.length > 0}
  <Replay {replay} />
{/if}
