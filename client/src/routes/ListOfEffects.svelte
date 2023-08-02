<script lang="ts">
  import { onMount } from 'svelte'
  import { _ } from 'svelte-i18n'

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
