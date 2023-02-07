import type { Energy } from './common'
import { shuffle } from './utils'

const ENERGY_POOL: Energy[] = [
  ...new Array(13).fill('red'),
  ...new Array(13).fill('black'),
  ...new Array(13).fill('blue'),
  ...new Array(13).fill('yellow'),
]
export function init_energy_pool() {
  return shuffle(ENERGY_POOL)
}
