export enum BuildMethod {
  DIRECTLY,
  FROM_RESEARCH,
  FROM_FILED,
}

export const ALL_ENERGY_TYPES = ['red', 'blue', 'black', 'yellow'] as const
export const ALL_GIZMO_LEVELS = [0, 1, 2, 3] as const
export const GIZMO_LEVELS = [1, 2, 3] as const
export const ALL_BUILD_METHODS = [
  BuildMethod.DIRECTLY,
  BuildMethod.FROM_FILED,
  BuildMethod.FROM_RESEARCH,
]

export type AllGizmoLevel = typeof ALL_GIZMO_LEVELS[number]
export type GizmoLevel = typeof GIZMO_LEVELS[number]
export type Energy = typeof ALL_ENERGY_TYPES[number]
export type EnergyWithAny = Energy | 'any'

export enum Stage {
  MAIN = 'MAIN',
  RESEARCH = 'RESEARCH',
  TRIGGER = 'TRIGGER',
  EXTRA_PICK = 'EXTRA_PICK',
  EXTRA_BUILD = 'EXTRA_BUILD',
  EXTRA_FILE = 'EXTRA_FILE',
  EXTRA_RESEARCH = 'EXTRA_RESEARCH',
  GAME_OVER = 'GAME_OVER',
}
