<script lang="ts">
  import { onDestroy } from 'svelte'
  import { random_int } from 'gizmos-env/utils'
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
    sample,
  } = client

  const { player_index, env, observation } = game

  let name = `player${random_int(100)}`

  onDestroy(() => {
    client.destroy()
  })

  let auto = false
  $: if (
    auto &&
    $env &&
    $player_index === $observation?.curr_player_index &&
    $env.action_space.length > 0
  ) {
    console.log(sample())
  }
</script>

<div>
  Connection status: <span
    class:status-red={$socket_status === 'red'}
    class:status-green={$socket_status === 'green'}
  >
    {$socket_status}
  </span>
</div>
<div>
  auto
  <input type="checkbox" bind:value={auto} />
</div>
{#if !$observation}
  <input bind:value={name} />
  <button class="btn" on:click={() => login(name)}>login as {name}</button>
  {#if $in_room}
    <button class="btn" on:click={() => ready()}>ready</button>
  {/if}
  <ul>
    {#each $room_info as info}
      <li>{info.name} {info.ready ? '(ready)' : ''}</li>
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
