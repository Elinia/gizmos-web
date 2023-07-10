<script lang="ts">
  import { onDestroy } from 'svelte'
  import { _ } from 'svelte-i18n'
  import { random_int } from 'gizmos-env/utils'
  import LocaleSwitch from './LocaleSwitch.svelte'
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
  <LocaleSwitch />
  <div>
    {$_('connection_status.title')}:
    <span
      class:status-red={$socket_status === 'red'}
      class:status-green={$socket_status === 'green'}
    >
      {$_(`connection_status.value.${$socket_status}`)}
    </span>
  </div>
  {#if !$observation}
    <div>
      <input bind:value={name} />
      <button class="btn" on:click={() => login(name)}>
        {$_('join_as', { values: { name } })}
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
