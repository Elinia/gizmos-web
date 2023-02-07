<script>
  import '../app.postcss'
</script>

<slot />

<style global lang="postcss">
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
</style>
