<script lang="ts">
  import type { GizmosEnv } from 'gizmos-env/GizmosEnv'
  import type { PlayerInfo } from 'gizmos-env/Player'
  import Energy from './Energy.svelte'

  export let player: PlayerInfo
  export let env: GizmosEnv
</script>

<div class="flex gap-2">
  <div class="font-bold" title="estimated score">🏆: {player.score}</div>
  <div>
    <span title="Gizmos count">
      ✨: {player.gizmos.length}/{env.max_gizmos_num}
    </span>
    <span title="Level3 Gizmos count">
      ({player.level3_gizmos.length}/{env.max_level3_gizmos_num})
    </span>
  </div>
  <div title="Point token">⭐: {player.point_token}</div>
  <div title="Filed gizmos">📁:{player.filed.length}/{player.max_file_num}</div>
  <div title="Research number">🔍:{player.research_num}</div>
  <div class="energy" title="energy">
    🔮 ({player.total_energy_num}/{player.max_energy_num}):
    <Energy energy_num={player.energy_num} />
  </div>
</div>
