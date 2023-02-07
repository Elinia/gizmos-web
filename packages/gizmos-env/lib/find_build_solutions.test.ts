import { find_build_solutions } from './find_build_solutions'
import { converter_double_level3, converter_level1 } from './gizmos_pool'
import { init_energy_num } from './gizmos_utils'

test('find_build_solutions', () => {
  expect(
    find_build_solutions('red', 1, init_energy_num({ red: 1 }), [], false)
  ).toHaveLength(1)
  expect(
    find_build_solutions('red', 1, init_energy_num({ red: 2 }), [], false)
  ).toHaveLength(1)

  const gizmo1 = converter_level1('red', 'yellow')
  const gizmo2 = converter_double_level3('red', ['blue', 'yellow'])
  const solutions = find_build_solutions(
    'blue',
    6,
    init_energy_num({ blue: 4, yellow: 1 }),
    [gizmo1, gizmo2],
    false
  )
  expect(solutions.length).toBe(1)
  const { energy_num, gizmos } = solutions[0]
  expect(energy_num).toEqual(init_energy_num({ blue: 4, yellow: 1 }))
  expect(new Set(gizmos)).toEqual(new Set([gizmo1, gizmo2]))
})
