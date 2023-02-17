import { find_build_solutions } from './find_build_solutions'
import {
  converter_any_level2,
  converter_any_level3,
  converter_double_level2,
  converter_double_level3,
  converter_level1,
} from './gizmos_pool'
import { init_energy_num } from './gizmos_utils'

describe('find_build_solutions', () => {
  test('basic without converter', () => {
    expect(
      find_build_solutions('red', 1, init_energy_num({ red: 1 }), [], false)
    ).toHaveLength(1)
    expect(
      find_build_solutions('red', 1, init_energy_num({ red: 2 }), [], false)
    ).toHaveLength(1)
  })

  test('basic double & any converter', () => {
    const g1 = converter_level1('red', 'yellow')
    const g2 = converter_double_level3('red', ['blue', 'yellow'])
    const solutions = find_build_solutions(
      'blue',
      6,
      init_energy_num({ blue: 4, yellow: 1 }),
      [g1, g2],
      false
    )
    expect(solutions.length).toBe(1)
    const { energy_num, gizmos } = solutions[0]
    expect(energy_num).toEqual(init_energy_num({ blue: 4, yellow: 1 }))
    expect(new Set(gizmos)).toEqual(new Set([g1, g2]))
  })

  test('any to any & formulae length > 1', () => {
    const g1 = converter_level1('red', 'blue')
    const g2 = converter_any_level2('red', 'red')
    const g3 = converter_any_level3('red')
    const solutions = find_build_solutions(
      'black',
      6,
      init_energy_num({ red: 2, blue: 2, black: 2 }),
      [g1, g2, g3],
      false
    )
    expect(solutions.length).toBe(1)
    const { energy_num, gizmos } = solutions[0]
    expect(energy_num).toEqual(init_energy_num({ red: 2, black: 2, blue: 2 }))
    expect(new Set(gizmos)).toEqual(new Set([g1, g2, g3]))
  })

  test('build any', () => {
    const g1 = converter_level1('red', 'blue')
    const g2 = converter_any_level2('red', 'red')
    const g3 = converter_any_level3('red')
    const solutions = find_build_solutions(
      'any',
      6,
      init_energy_num({ red: 2, blue: 2, black: 2 }),
      [g1, g2, g3],
      false
    )
    expect(solutions.length).toBe(1)
    const { energy_num, gizmos } = solutions[0]
    expect(energy_num).toEqual(init_energy_num({ red: 2, black: 2, blue: 2 }))
    expect(new Set(gizmos)).toEqual(new Set([]))
  })

  test('build any with double', () => {
    const g1 = converter_double_level2('red', 'red')
    const g2 = converter_double_level3('red', ['blue', 'yellow'])
    const solutions = find_build_solutions(
      'any',
      6,
      init_energy_num({ red: 1, blue: 1, yellow: 2 }),
      [g1, g2],
      false
    )
    expect(solutions.length).toBe(2)
    const { energy_num, gizmos } = solutions.find(
      s => s.energy_num.yellow === 1
    )!
    expect(energy_num).toEqual(init_energy_num({ red: 1, yellow: 1, blue: 1 }))
    expect(new Set(gizmos)).toEqual(new Set([g1, g2]))
  })

  test('complex', () => {
    const g1 = converter_any_level3('red')
    const g2 = converter_double_level3('red', ['blue', 'yellow'])
    const g3 = converter_any_level2('red', 'blue')
    const g4 = converter_level1('red', 'yellow')
    const g5 = converter_any_level2('red', 'black')

    const solutions = find_build_solutions(
      'black',
      5,
      init_energy_num({ black: 3 }),
      [g1, g2, g3, g4, g5],
      false
    )
    expect(solutions.length).toBe(1)

    const solutions2 = find_build_solutions(
      'red',
      5,
      init_energy_num({ red: 1, black: 2 }),
      [g1, g2, g3, g4, g5],
      false
    )
    expect(solutions2.length).toBe(1)

    const solutions3 = find_build_solutions(
      'black',
      5,
      init_energy_num({ black: 2, red: 1 }),
      [g1, g2, g3, g4, g5],
      false
    )
    expect(solutions3.length).toBe(0)
  })

  test('build any', () => {
    const solutions = find_build_solutions(
      'any',
      7,
      init_energy_num({ red: 5, blue: 1, black: 1 }),
      [],
      false
    )
    expect(solutions.length).toBe(1)
  })
})
