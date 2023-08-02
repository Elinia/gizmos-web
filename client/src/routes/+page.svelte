<script lang="ts">
  import { onDestroy } from 'svelte'
  import { _ } from 'svelte-i18n'
  import { random_int } from 'gizmos-env/utils'
  import LocaleSwitch from './LocaleSwitch.svelte'
  import RuleBook from './RuleBook.svelte'
  import ListOfEffects from './ListOfEffects.svelte'
  import Game from './Game.svelte'
  import { GizmosClient } from '$lib/client.js'

  const client = new GizmosClient()
  const {
    pending,
    socket_status,
    game_ongoing,
    room_info,
    in_room,
    login,
    ready,
    game,
    pick,
    file,
    file_from_research,
    build,
    build_from_filed,
    build_from_research,
    research,
    use_gizmo,
    give_up,
    end,
    replay,
  } = client

  const { observation } = game

  let name = `player${random_int(100)}`

  onDestroy(() => {
    client.destroy()
  })
</script>

<div class="flex flex-col gap-2">
  <div class="text-center text-2xl font-bold">{$_('gizmos')}</div>
  <div class="flex justify-center gap-2">
    <RuleBook /> | <ListOfEffects />
  </div>
  {#if !$observation}
    <div class="flex gap-2">
      <input class="shrink" bind:value={name} />
      <button class="btn" on:click={() => login(name)}>
        {$_('join')}
      </button>
      {#if $in_room}
        <button class="btn" on:click={() => ready()}>{$_('ready')}</button>
      {/if}
    </div>
    <ul>
      {#each $room_info as info}
        <li>{info.name} {info.ready ? `(${$_('ready')})` : ''}</li>
      {/each}
      <li />
    </ul>
  {/if}
  <Game
    ongoing={$game_ongoing}
    {game}
    {pending}
    {pick}
    {file}
    {file_from_research}
    {build}
    {build_from_filed}
    {build_from_research}
    {research}
    {use_gizmo}
    {give_up}
    {end}
  />
  {#if $replay}
    {@const blob = new Blob([JSON.stringify($replay, null, 2)], {
      type: 'application/json',
    })}
    {@const url = URL.createObjectURL(blob)}
    <a href={url} download="replay.json">{$_('replay')}</a>
  {/if}
  <div class="fixed bottom-0 w-full px-2 flex justify-between bg-lime-100">
    <div>
      {$_('connection_status.title')}:
      <span
        class:status-red={$socket_status === 'red'}
        class:status-green={$socket_status === 'green'}
      >
        {$_(`connection_status.value.${$socket_status}`)}
      </span>
    </div>
    <LocaleSwitch />
  </div>
</div>

<style lang="postcss">
  .status-red {
    @apply text-red-500;
  }
  .status-green {
    @apply text-green-500;
  }
  input {
    @apply border border-transparent border-b-blue-300 outline-none;
  }
  button.btn {
    @apply rounded-md bg-blue-300 p-1;
  }
</style>
