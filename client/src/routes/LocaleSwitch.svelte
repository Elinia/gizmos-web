<script lang="ts">
  import { locale } from 'svelte-i18n'
</script>

<div>
  <button disabled={$locale == 'en-US'} on:click={() => locale.set('en-US')}
    >EN</button
  >
  /
  <button disabled={$locale == 'zh-CN'} on:click={() => locale.set('zh-CN')}
    >中文</button
  >
</div>

<style lang="postcss">
  button:disabled {
    @apply font-bold;
  }
  button:not(:disabled) {
    color: blueviolet;
  }
</style>
