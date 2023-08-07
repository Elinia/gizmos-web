<script lang="ts">
  import '@unocss/reset/tailwind.css'
</script>

<slot />

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
