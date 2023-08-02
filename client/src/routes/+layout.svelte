<script lang="ts">
  import '../app.postcss'
  import { onMount } from 'svelte'

  const sm = window.matchMedia('(0rem <= width < 48rem)')
  const md = window.matchMedia('(48rem <= width < 72rem)')
  const lg = window.matchMedia('(width >= 72rem)')
  const to_sm = (e: { matches: boolean }) => {
    if (e.matches) size = 'sm'
  }
  const to_md = (e: { matches: boolean }) => {
    if (e.matches) size = 'md'
  }
  const to_lg = (e: { matches: boolean }) => {
    if (e.matches) size = 'lg'
  }

  let size = ''

  onMount(() => {
    to_sm(sm)
    to_md(md)
    to_lg(lg)
    sm.addEventListener('change', to_sm)
    md.addEventListener('change', to_md)
    lg.addEventListener('change', to_lg)

    return () => {
      sm.removeEventListener('change', to_sm)
      md.removeEventListener('change', to_md)
      lg.removeEventListener('change', to_lg)
    }
  })
</script>

<div class={size}>
  <slot />
</div>

<style global lang="postcss">
  body {
    @apply relative min-h-screen;
  }

  .red {
    @apply bg-red-500;
  }
  .yellow {
    @apply bg-yellow-500;
  }
  .blue {
    @apply bg-blue-500;
  }
  .black {
    @apply bg-black;
  }
  .any {
    @apply bg-gradient-to-r from-red-500 via-yellow-500 to-blue-500;
  }

  .energy,
  .gizmos,
  .gizmos-simple {
    @apply flex items-center gap-2 flex-wrap;
  }

  .gizmos {
    @apply min-h-[72px];
  }

  .avail {
    @apply outline outline-2 outline-red-500/50 -outline-offset-1;
  }

  dialog {
    @apply p-4 rounded-lg;
  }
</style>
