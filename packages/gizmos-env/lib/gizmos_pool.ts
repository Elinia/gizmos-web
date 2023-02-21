import {
  BuildMethod,
  type AllGizmoLevel,
  type Energy,
  type GizmoLevel,
} from './common'
import {
  BuildGizmo,
  ConverterGizmo,
  FileGizmo,
  Gizmo,
  PickGizmo,
  UpgradeGizmo,
} from './Gizmo'
import { shuffle } from './utils'

let id = 0

export function file_draw_level0() {
  return new FileGizmo({
    id: id++,
    level: 0 as AllGizmoLevel,
    energy_type: 'any',
    energy_cost: 0,
    value: 0,
    effect: {
      type: 'free_draw',
      num: 1,
    },
  })
}

export function init_level0() {
  return [
    file_draw_level0(),
    file_draw_level0(),
    file_draw_level0(),
    file_draw_level0(),
  ]
}

const LEVEL1_COMMON = {
  level: 1 as GizmoLevel,
  energy_cost: 1,
  value: 1,
}

const BUILD_COMMON = {
  level: 'any',
  method: 'any',
} as const

export function build_point_level1(energy_type: Energy, build_energy: Energy) {
  return new BuildGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: [build_energy],
    },
    effect: {
      type: 'add_point_token',
      num: 1,
    },
  })
}

export function build_pick_level1(energy_type: Energy, build_energy: Energy) {
  return new BuildGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: [build_energy],
    },
    effect: {
      type: 'free_pick',
      num: 1,
    },
  })
}

export function upgrade_ef_level1(energy_type: Energy) {
  return new UpgradeGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    max_energy_num: 1,
    max_file_num: 1,
  })
}

export function upgrade_er_level1(energy_type: Energy) {
  return new UpgradeGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    max_energy_num: 1,
    research_num: 1,
  })
}

export function file_pick_level1(energy_type: Energy) {
  return new FileGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    effect: {
      type: 'free_pick',
      num: 1,
    },
  })
}

export function pick_draw_level1(energy_type: Energy, pick_energy: Energy) {
  return new PickGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    when_pick: [pick_energy],
    effect: {
      type: 'free_draw',
      num: 1,
    },
  })
}

export function converter_level1(energy_type: Energy, from_energy: Energy) {
  return new ConverterGizmo({
    id: id++,
    ...LEVEL1_COMMON,
    energy_type,
    formulae: [
      {
        from: {
          energy: from_energy,
          num: 1,
        },
        to: {
          energy: 'any',
          num: 1,
        },
      },
    ],
  })
}

export function init_level1(): Gizmo[] {
  return [
    build_point_level1('yellow', 'blue'),
    build_point_level1('blue', 'black'),
    build_point_level1('black', 'red'),
    build_point_level1('red', 'yellow'),
    build_pick_level1('red', 'black'),
    build_pick_level1('black', 'blue'),
    build_pick_level1('blue', 'yellow'),
    build_pick_level1('yellow', 'red'),
    upgrade_ef_level1('red'),
    upgrade_ef_level1('black'),
    upgrade_ef_level1('blue'),
    upgrade_ef_level1('yellow'),
    upgrade_er_level1('red'),
    upgrade_er_level1('black'),
    upgrade_er_level1('blue'),
    upgrade_er_level1('yellow'),
    file_pick_level1('red'),
    file_pick_level1('black'),
    file_pick_level1('blue'),
    file_pick_level1('yellow'),
    pick_draw_level1('yellow', 'red'),
    pick_draw_level1('red', 'blue'),
    pick_draw_level1('blue', 'black'),
    pick_draw_level1('black', 'yellow'),
    pick_draw_level1('blue', 'red'),
    pick_draw_level1('red', 'yellow'),
    pick_draw_level1('yellow', 'black'),
    pick_draw_level1('black', 'blue'),
    converter_level1('red', 'blue'),
    converter_level1('red', 'black'),
    converter_level1('yellow', 'blue'),
    converter_level1('yellow', 'black'),
    converter_level1('blue', 'red'),
    converter_level1('blue', 'yellow'),
    converter_level1('black', 'red'),
    converter_level1('black', 'yellow'),
  ]
}

export function level2_common(cost: number) {
  return {
    level: 2 as GizmoLevel,
    energy_cost: cost,
    value: cost,
  }
}

export function converter_double_level2(
  energy_type: Energy,
  from_energy: Energy
) {
  return new ConverterGizmo({
    id: id++,
    ...level2_common(3),
    energy_type,
    formulae: [
      {
        from: {
          energy: from_energy,
          num: 1,
        },
        to: {
          energy: from_energy,
          num: 2,
        },
      },
    ],
  })
}

export function converter_any_level2(energy_type: Energy, from_energy: Energy) {
  return new ConverterGizmo({
    id: id++,
    ...level2_common(2),
    energy_type,
    formulae: [
      {
        from: {
          energy: from_energy,
          num: 1,
        },
        to: {
          energy: 'any',
          num: 1,
        },
      },
      {
        from: {
          energy: from_energy,
          num: 1,
        },
        to: {
          energy: 'any',
          num: 1,
        },
      },
    ],
  })
}

export function build_pick_level2(energy_type: Energy, build_energy: Energy[]) {
  return new BuildGizmo({
    id: id++,
    ...level2_common(2),
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: build_energy,
    },
    effect: {
      type: 'free_pick',
      num: 1,
    },
  })
}

export function build_point_level2(
  energy_type: Energy,
  build_energy: Energy[]
) {
  return new BuildGizmo({
    id: id++,
    ...level2_common(3),
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: build_energy,
    },
    effect: {
      type: 'add_point_token',
      num: 1,
    },
  })
}

export function build_from_file_pick_level2(energy_type: Energy) {
  return new BuildGizmo({
    id: id++,
    ...level2_common(3),
    energy_type,
    when_build: {
      level: 'any',
      method: [BuildMethod.FROM_FILED],
      energy: 'any',
    },
    effect: {
      type: 'free_pick',
      num: 2,
    },
  })
}

export function pick_draw_level2(energy_type: Energy, pick_energy: Energy[]) {
  return new PickGizmo({
    id: id++,
    ...level2_common(2),
    energy_type,
    when_pick: pick_energy,
    effect: {
      type: 'free_draw',
      num: 1,
    },
  })
}

export function upgrade_level2(energy_type: Energy) {
  return new UpgradeGizmo({
    id: id++,
    ...level2_common(3),
    energy_type,
    max_energy_num: 2,
    max_file_num: 1,
    research_num: 2,
  })
}

export function init_level2() {
  return [
    converter_double_level2('red', 'black'),
    converter_double_level2('black', 'red'),
    converter_double_level2('yellow', 'blue'),
    converter_double_level2('blue', 'yellow'),
    converter_double_level2('red', 'blue'),
    converter_double_level2('blue', 'red'),
    converter_double_level2('yellow', 'black'),
    converter_double_level2('black', 'yellow'),
    converter_any_level2('yellow', 'red'),
    converter_any_level2('red', 'yellow'),
    converter_any_level2('blue', 'black'),
    converter_any_level2('black', 'blue'),
    build_pick_level2('blue', ['yellow', 'black']),
    build_pick_level2('blue', ['yellow', 'red']),
    build_pick_level2('yellow', ['black', 'red']),
    build_pick_level2('yellow', ['blue', 'black']),
    build_pick_level2('red', ['blue', 'yellow']),
    build_pick_level2('red', ['blue', 'black']),
    build_pick_level2('black', ['red', 'blue']),
    build_pick_level2('black', ['yellow', 'red']),
    build_point_level2('yellow', ['red', 'blue']),
    build_point_level2('red', ['yellow', 'black']),
    build_point_level2('black', ['blue', 'yellow']),
    build_point_level2('blue', ['black', 'red']),
    build_from_file_pick_level2('black'),
    build_from_file_pick_level2('blue'),
    build_from_file_pick_level2('red'),
    build_from_file_pick_level2('yellow'),
    pick_draw_level2('yellow', ['red', 'blue']),
    pick_draw_level2('red', ['blue', 'black']),
    pick_draw_level2('blue', ['yellow', 'black']),
    pick_draw_level2('black', ['yellow', 'red']),
    upgrade_level2('black'),
    upgrade_level2('blue'),
    upgrade_level2('red'),
    upgrade_level2('yellow'),
  ]
}

export function level3_common(cost: number) {
  return {
    level: 3 as GizmoLevel,
    energy_cost: cost,
    value: cost,
  }
}

export function upgrade_e_level3(energy_type: Energy) {
  return new UpgradeGizmo({
    id: id++,
    ...level3_common(4),
    energy_type,
    max_energy_num: 4,
  })
}

export function upgrade_forbid_file_level3(energy_type: Energy) {
  return new UpgradeGizmo({
    id: id++,
    level: 3,
    energy_cost: 4,
    value: 7,
    energy_type,
    max_file_num: -Infinity,
  })
}

export function upgrade_forbid_research_level3(energy_type: Energy) {
  return new UpgradeGizmo({
    id: id++,
    level: 3,
    energy_cost: 4,
    value: 8,
    energy_type,
    research_num: -Infinity,
  })
}

export function upgrade_token_as_point_level3() {
  return new UpgradeGizmo({
    id: id++,
    level: 3,
    energy_type: 'any',
    energy_cost: 7,
    value: 0,
    effect: {
      type: 'token_as_point',
    },
  })
}

export function upgrade_energy_as_point_level3() {
  return new UpgradeGizmo({
    id: id++,
    level: 3,
    energy_type: 'any',
    energy_cost: 7,
    value: 0,
    effect: {
      type: 'energy_as_point',
    },
  })
}

export function upgrade_build_from_filed_cost_reduction_level3(
  energy_type: Energy
) {
  return new UpgradeGizmo({
    id: id++,
    ...level3_common(5),
    energy_type,
    build_from_filed_cost_reduction: 1,
  })
}

export function upgrade_build_from_research_cost_reduction_level3(
  energy_type: Energy
) {
  return new UpgradeGizmo({
    id: id++,
    ...level3_common(6),
    energy_type,
    build_from_research_cost_reduction: 1,
  })
}

export function file_draw_level3(energy_type: Energy) {
  return new FileGizmo({
    id: id++,
    ...level3_common(4),
    energy_type,
    effect: {
      type: 'free_draw',
      num: 3,
    },
  })
}

export function file_point_level3(energy_type: Energy) {
  return new FileGizmo({
    id: id++,
    ...level3_common(4),
    energy_type,
    effect: {
      type: 'add_point_token',
      num: 1,
    },
  })
}

export function build_point_level3(
  energy_type: Energy,
  build_energy: Energy[]
) {
  return new BuildGizmo({
    id: id++,
    ...level3_common(5),
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: build_energy,
    },
    effect: {
      type: 'add_point_token',
      num: 2,
    },
  })
}

export function build_pick_level3(energy_type: Energy) {
  return new BuildGizmo({
    id: id++,
    ...level3_common(6),
    energy_type,
    when_build: {
      level: [2],
      energy: 'any',
      method: 'any',
    },
    effect: {
      type: 'free_pick',
      num: 2,
    },
  })
}

export function build_from_file_point_level3(energy_type: Energy) {
  return new BuildGizmo({
    id: id++,
    ...level3_common(5),
    energy_type,
    when_build: {
      level: 'any',
      method: [BuildMethod.FROM_FILED],
      energy: 'any',
    },
    effect: {
      type: 'add_point_token',
      num: 2,
    },
  })
}

export function build_file_level3(energy_type: Energy, build_energy: Energy[]) {
  return new BuildGizmo({
    id: id++,
    ...level3_common(5),
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: build_energy,
    },
    effect: {
      type: 'extra_file',
    },
  })
}

export function build_research_level3(
  energy_type: Energy,
  build_energy: Energy[]
) {
  return new BuildGizmo({
    id: id++,
    ...level3_common(7),
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: build_energy,
    },
    effect: {
      type: 'extra_research',
    },
  })
}

export function build_build_level3(
  energy_type: Energy,
  build_energy: Energy[]
) {
  return new BuildGizmo({
    id: id++,
    ...level3_common(6),
    energy_type,
    when_build: {
      ...BUILD_COMMON,
      energy: build_energy,
    },
    effect: {
      type: 'extra_build',
      level: [1],
    },
  })
}

export function converter_double_level3(
  energy_type: Energy,
  from_energy: Energy[]
) {
  return new ConverterGizmo({
    id: id++,
    ...level3_common(5),
    energy_type,
    formulae: from_energy.map(from => ({
      from: {
        energy: from,
        num: 1,
      },
      to: {
        energy: from,
        num: 2,
      },
    })),
  })
}

export function converter_any_level3(energy_type: Energy) {
  return new ConverterGizmo({
    id: id++,
    ...level3_common(4),
    energy_type,
    formulae: [
      {
        from: {
          energy: 'any',
          num: 1,
        },
        to: {
          energy: 'any',
          num: 1,
        },
      },
    ],
  })
}

export function converter_cost_reduction_level3(energy_type: Energy) {
  return new ConverterGizmo({
    id: id++,
    ...level3_common(5),
    energy_type,
    prerequisite: {
      level: [2],
    },
    formulae: [
      {
        from: {
          energy: 'any',
          num: 0,
        },
        to: {
          energy: 'any',
          num: 1,
        },
      },
    ],
  })
}

export function init_level3() {
  return [
    upgrade_e_level3('blue'),
    upgrade_e_level3('black'),
    upgrade_forbid_file_level3('red'),
    upgrade_forbid_file_level3('blue'),
    upgrade_forbid_research_level3('yellow'),
    upgrade_forbid_research_level3('black'),
    upgrade_energy_as_point_level3(),
    upgrade_energy_as_point_level3(),
    upgrade_token_as_point_level3(),
    upgrade_token_as_point_level3(),
    upgrade_build_from_filed_cost_reduction_level3('red'),
    upgrade_build_from_filed_cost_reduction_level3('blue'),
    upgrade_build_from_research_cost_reduction_level3('yellow'),
    upgrade_build_from_research_cost_reduction_level3('black'),
    file_draw_level3('yellow'),
    file_draw_level3('blue'),
    file_point_level3('red'),
    file_point_level3('black'),
    build_point_level3('red', ['yellow', 'black']),
    build_point_level3('black', ['red', 'blue']),
    build_pick_level3('red'),
    build_pick_level3('black'),
    build_from_file_point_level3('yellow'),
    build_from_file_point_level3('red'),
    build_file_level3('yellow', ['black', 'red']),
    build_file_level3('black', ['blue', 'yellow']),
    build_research_level3('red', ['blue', 'black']),
    build_research_level3('blue', ['yellow', 'red']),
    build_build_level3('yellow', ['blue', 'black']),
    build_build_level3('blue', ['yellow', 'red']),
    converter_double_level3('blue', ['black', 'red']),
    converter_double_level3('black', ['blue', 'yellow']),
    converter_any_level3('red'),
    converter_any_level3('yellow'),
    converter_cost_reduction_level3('yellow'),
    converter_cost_reduction_level3('blue'),
  ]
}

const l0 = init_level0()
const l1 = init_level1()
const l2 = init_level2()
const l3 = init_level3()
const gizmos = [...l0, ...l1, ...l2, ...l3]
gizmos.forEach((g, i) => {
  if (g.id !== i) {
    throw new Error('id inconsistent')
  }
})

export function init_gizmos() {
  gizmos.forEach(g => g.reset())
  return {
    gizmos,
    gizmos_pool: {
      1: shuffle(l1),
      2: shuffle(l2),
      3: shuffle(l3).slice(0, 16),
    },
  }
}
