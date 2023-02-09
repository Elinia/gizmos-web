<script lang="ts">
  import { onDestroy } from 'svelte'
  import {
    ALL_ENERGY_TYPES,
    BuildMethod,
    type GizmoLevel,
  } from 'gizmos-env/common'
  import { ActionType } from 'gizmos-env/GizmosEnv'
  import type { BuildSolution, PlayerInfo } from 'gizmos-env/Player'
  import { random_int } from 'gizmos-env/utils'
  import Gizmo from './Gizmo.svelte'
  import { render_level } from '$lib/helpers.js'
  import { GizmosClient } from '$lib/client.js'

  const client = new GizmosClient()
  const {
    log,
    socket_status,
    game_ongoing,
    room_info,
    player_list,
    player_index,
    me,
    login,
    ready,
    env,
    observation,
    drop_energy_num,
    is_avail,
    pick,
    select_drop,
    drop,
    file,
    file_from_research,
    build,
    build_from_file,
    build_from_research,
    research,
    use_gizmo_id,
    give_up,
    end,
    sample,
  } = client

  $: console.log($observation, $env)

  $: total_drop_energy_num = Object.values($drop_energy_num).reduce(
    (acc, curr) => acc + curr,
    0
  )

  const LEVELS: GizmoLevel[] = [3, 2, 1]

  let build_dialog_element: HTMLDialogElement
  let build_dialog: {
    method: BuildMethod
    level: GizmoLevel
    index: number
    solutions: BuildSolution[]
  } | null = null

  function on_build(me: PlayerInfo | null, solution: BuildSolution) {
    if (!me || !build_dialog) return
    const common_params = [
      build_dialog.index,
      solution.energy_num,
      solution.gizmos.map(g => me.gizmos.findIndex(_g => g.id === _g.id)),
    ] as const
    switch (build_dialog.method) {
      case BuildMethod.DIRECTLY:
        build(build_dialog.level, ...common_params)
        break
      case BuildMethod.FROM_FILED:
        build_from_file(...common_params)
        break
      case BuildMethod.FROM_RESEARCH:
        build_from_research(...common_params)
        break
      default:
        throw new Error('unexpected build method')
    }
  }

  let research_dialog_element: HTMLDialogElement
  $: if (research_dialog_element && $observation?.researching) {
    research_dialog_element.showModal()
  }
  $: if (research_dialog_element && !$observation?.researching) {
    research_dialog_element.close()
  }

  $: if (build_dialog_element) {
    build_dialog_element.addEventListener('close', () => {
      build_dialog = null
    })
  }

  let name = `player${random_int(100)}`

  onDestroy(() => {
    client.destroy()
  })

  let auto = false
  $: if (
    auto &&
    $env &&
    $player_index === $observation?.curr_player_index &&
    $env.avail_actions.length > 0
  ) {
    setTimeout(() => sample(), 100)
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
  <button class="btn" on:click={() => ready()}>ready</button>
  <ul>
    {#each $room_info as info}
      <li>{info.name} {info.ready ? '(ready)' : ''}</li>
    {/each}
    <li />
  </ul>
{/if}
{#if $game_ongoing && $observation && $env && $me}
  {@const my_gizmos = [
    { label: '➕Upgrade', gizmos: $me.upgrade_gizmos },
    { label: '→Converter', gizmos: $me.converter_gizmos },
    { label: '📁File', gizmos: $me.file_gizmos },
    { label: '👌Pick', gizmos: $me.pick_gizmos },
    { label: '🔧Build', gizmos: $me.build_gizmos },
  ]}
  <div>
    <span>Stage: {$observation.curr_stage}</span>
    <span>
      Current player: {$player_list[$observation.curr_player_index].name}
    </span>
  </div>

  <div>Point token: {$me.point_token}</div>
  <div class="flex gap-2" class:avail={$is_avail[ActionType.DROP]}>
    <div class="energy">
      Energy ({$me.total_energy_num -
        total_drop_energy_num}/{$me.max_energy_num}):
      {#each ALL_ENERGY_TYPES as energy}
        {@const num = $me.energy_num[energy]}
        {@const remain_num = num - $drop_energy_num[energy]}
        {#each new Array(remain_num).fill(energy) as e}
          <button
            class={`w-5 h-5 rounded-full ${e}`}
            on:click={() => remain_num > 0 && select_drop(e)}
          />
        {/each}
      {/each}
    </div>
    {#if $is_avail[ActionType.DROP]}
      {@const ready_to_drop =
        $me.total_energy_num - total_drop_energy_num === $me.max_energy_num}
      <div class="energy">
        Drop energy:
        {#each ALL_ENERGY_TYPES as energy}
          {@const num = $drop_energy_num[energy]}
          {#each new Array(num).fill(energy) as e}
            <button
              class={`w-5 h-5 rounded-full ${e}`}
              on:click={() => select_drop(e, -1)}
            />
          {/each}
        {/each}
        <button
          class:avail={ready_to_drop}
          disabled={!ready_to_drop}
          on:click={() => drop()}
        >
          Drop
        </button>
      </div>
    {/if}
  </div>
  <div>
    File ({$me.filed.length}/{$me.max_file_num > 0
      ? $me.max_file_num
      : 'forbidden'}):
    <div class="gizmos">
      {#each $me.filed as g, index}
        {@const gizmo = $env.gizmo(g.id)}
        {@const solutions = $is_avail[ActionType.BUILD_FROM_FILED]
          ? $env.build_solutions(gizmo, BuildMethod.FROM_FILED)
          : []}
        {@const can_build = solutions.length > 0}
        <div>
          <Gizmo info={gizmo} />
          <button
            class:avail={can_build}
            disabled={!can_build}
            on:click={() => {
              build_dialog = {
                level: gizmo.level,
                index,
                method: BuildMethod.FROM_FILED,
                solutions,
              }
              build_dialog_element.showModal()
            }}
          >
            🔧
          </button>
        </div>
      {/each}
    </div>
  </div>
  <div>
    Gizmos ({$me.gizmos.length}/{$env.max_gizmos_num} Level3 {$me.level3_gizmos
      .length}/{$env.max_level3_gizmos_num}) :
    {#each my_gizmos as { label, gizmos }}
      <div>{label}:</div>
      <div class="gizmos-simple">
        {#each gizmos as gizmo}
          {@const can_use = $is_avail[ActionType.USE_GIZMO] && gizmo.active}
          <button
            class:avail={can_use}
            disabled={!can_use}
            on:click={() => use_gizmo_id(gizmo.id)}
          >
            <Gizmo info={gizmo} />
          </button>
        {/each}
      </div>
    {/each}
  </div>
  <div>
    <button
      class:avail={$is_avail[ActionType.GIVE_UP]}
      disabled={!$is_avail[ActionType.GIVE_UP]}
      on:click={() => give_up()}
    >
      Give up
    </button>
    <button
      class:avail={$is_avail[ActionType.END]}
      disabled={!$is_avail[ActionType.END]}
      on:click={() => end()}
    >
      End turn
    </button>
  </div>
  Board:
  <div class="m-10 flex flex-col gap-2 items-center">
    <div class:avail={$is_avail[ActionType.PICK]}>
      Pick energy:
      <div class="energy">
        {#each $observation.energy_board as energy, i}
          <button
            class={`w-5 h-5 rounded-full ${energy}`}
            on:click={() => pick(i)}
          />
        {/each}
      </div>
    </div>
    {#each LEVELS as level}
      <div class="gizmos justify-center">
        <button
          class="w-36"
          class:avail={$is_avail[ActionType.RESEARCH]}
          disabled={!$is_avail[ActionType.RESEARCH]}
          on:click={() => research(level)}
        >
          <div>{render_level(level)}</div>
          <div>🔍: {$me.research_num}</div>
        </button>
        {#each $observation.gizmos_board[level] as g, index}
          {@const solutions = $is_avail[ActionType.BUILD]
            ? $env.build_solutions(g.id, BuildMethod.DIRECTLY)
            : []}
          {@const can_build = solutions.length > 0}
          <div>
            <Gizmo info={g} />
            <button
              class:avail={can_build}
              disabled={!can_build}
              on:click={() => {
                build_dialog = {
                  level,
                  index,
                  method: BuildMethod.DIRECTLY,
                  solutions,
                }
                build_dialog_element.showModal()
              }}
            >
              🔧
            </button>
            <button
              class:avail={$is_avail[ActionType.FILE]}
              disabled={!$is_avail[ActionType.FILE]}
              on:click={() => file(level, index)}
            >
              📁
            </button>
          </div>
        {/each}
      </div>
    {/each}
  </div>
  Players:
  {#each $observation.players as player, i}
    <div class="font-bold text-lg">
      {$player_list[i].name}
    </div>
    <div>
      ⭐:{player.point_token} 🔮:{player.total_energy_num}/{player.max_energy_num}
      📁:{player.filed.length}/{player.max_file_num} 🔍:{player.research_num}
    </div>
    <div>Estimated score: {player.score}</div>
    <div>
      Energy:
      {#each ALL_ENERGY_TYPES as energy}
        {@const num = player.energy_num[energy]}
        {#each new Array(num).fill(energy) as e}
          <button
            class={`w-5 h-5 rounded-full ${e}`}
            on:click={() => num > 0 && select_drop(e)}
          />
        {/each}
      {/each}
    </div>
    <div>
      Gizmos ({player.gizmos.length}/{$env.max_gizmos_num} Level3 {player
        .level3_gizmos.length}/{$env.max_level3_gizmos_num}):
    </div>
    <div class="gizmos-simple">
      {#each player.gizmos as gizmo}
        <Gizmo info={gizmo} simple={true} />
      {/each}
    </div>
    <div>
      File ({player.filed.length}/{player.max_file_num}):
    </div>
    <div class="gizmos-simple">
      {#each player.filed as gizmo}
        <Gizmo info={gizmo} />
      {/each}
    </div>
  {/each}
  <dialog bind:this={build_dialog_element}>
    <form method="dialog">
      {#if build_dialog}
        <div class="flex flex-col gap-2">
          {#each build_dialog.solutions as solution, i}
            <button class="avail" on:click={() => on_build($me, solution)}>
              Solution {i}:
              <div class="energy">
                Used energy:
                {#each ALL_ENERGY_TYPES as energy}
                  <span>{energy}: {solution.energy_num[energy]}</span>
                {/each}
              </div>
              <div class="gizmos-simple">
                Used gizmos:
                {#each solution.gizmos as gizmo}
                  <Gizmo info={gizmo} simple={true} />
                {/each}
              </div>
            </button>
          {/each}
        </div>
      {/if}
      <button value="cancel">Cancel</button>
    </form>
  </dialog>
  <dialog bind:this={research_dialog_element}>
    <form method="dialog">
      {#if $observation.researching}
        {@const level = $observation.researching.level}
        <div class="gizmos">
          {#each $observation.researching.gizmos as g, index}
            {@const gizmo = $env.gizmo(g.id)}
            {@const solutions = $is_avail[ActionType.BUILD_FROM_RESEARCH]
              ? $env.build_solutions(gizmo, BuildMethod.FROM_RESEARCH)
              : []}
            {@const can_build = solutions.length > 0}
            {@const can_file = $is_avail[ActionType.FILE_FROM_RESEARCH]}
            <div>
              <Gizmo info={gizmo} />
              <button
                class:avail={can_build}
                disabled={!can_build}
                on:click={() => {
                  build_dialog = {
                    level,
                    index,
                    method: BuildMethod.FROM_RESEARCH,
                    solutions,
                  }
                  build_dialog_element.showModal()
                }}
              >
                🔧
              </button>
              <button
                class:avail={can_file}
                disabled={!can_file}
                on:click={() => file_from_research(index)}
              >
                📁
              </button>
            </div>
          {/each}
        </div>
      {/if}
      {#if $is_avail[ActionType.GIVE_UP]}
        <button class="avail" value="cancel" on:click={() => give_up()}>
          Give up research
        </button>
      {/if}
    </form>
  </dialog>
{/if}
<div class="log">
  {#each $log as msg}
    <div>{msg}</div>
  {/each}
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

  .energy,
  .gizmos,
  .gizmos-simple {
    @apply flex gap-2 flex-wrap;
  }
  .gizmos {
    @apply h-[72px];
  }

  .gizmo {
    @apply border-2 border-black;
  }
  .avail {
    @apply outline outline-2 outline-red-500/50 -outline-offset-1;
  }
  .log {
    @apply resize-y h-80 m-2 p-2 overflow-auto bg-lime-100;
  }
</style>
