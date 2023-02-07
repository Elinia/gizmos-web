import type { Energy } from './common'

export function init_energy_num(energy_num?: Partial<Record<Energy, number>>) {
  return {
    red: 0,
    black: 0,
    blue: 0,
    yellow: 0,
    ...energy_num,
  }
}
