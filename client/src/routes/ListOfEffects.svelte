<script lang="ts">
  import { onMount } from 'svelte'
  import { _, locale } from 'svelte-i18n'

  let dialog: HTMLDialogElement

  function show_rule_book() {
    if (dialog.open) return
    dialog.showModal()
  }

  onMount(() => {
    const handler = (e: MouseEvent) => {
      if (!(e.target instanceof Element)) return
      if (e.target.id !== 'pdf') dialog.close()
    }
    dialog.addEventListener('click', handler)
    return () => {
      dialog.removeEventListener('click', handler)
    }
  })
</script>

<button on:click={show_rule_book}>{$_('list_of_effects')}</button>
<dialog bind:this={dialog}>
  {#if $locale === 'en-US'}
    <object
      title="list_of_effects"
      data="/ListOfEffects.pdf#toolbar=0"
      id="pdf"
      width="100%"
      height="100%"
    >
      <p>{$_('pdf_unsupported')}</p>
      <p>
        <a href="/ListOfEffects.pdf" download="ListOfEffects.pdf"
          >{$_('download')}</a
        >
      </p>
    </object>
  {:else if $locale === 'zh-CN'}
    <div class="flex flex-col gap-2">
      <img src="/e1.jpeg" alt="list of effects 1" />
      <img src="/e2.jpeg" alt="list of effects 2" />
    </div>
  {/if}
</dialog>

<style lang="postcss">
  dialog {
    width: 80%;
    height: 80%;
  }

  a {
    all: revert;
  }
</style>
