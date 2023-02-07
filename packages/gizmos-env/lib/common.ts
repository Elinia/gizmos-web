export enum BuildMethod {
  DIRECTLY,
  FROM_RESEARCH,
  FROM_FILED,
}

export const ALL_ENERGY_TYPES = ['red', 'blue', 'black', 'yellow'] as const
export const ALL_GIZMO_LEVELS = [0, 1, 2, 3] as const
export const ALL_BUILD_METHODS = [
  BuildMethod.DIRECTLY,
  BuildMethod.FROM_FILED,
  BuildMethod.FROM_RESEARCH,
]

export type AllGizmoLevel = typeof ALL_GIZMO_LEVELS[number]
export type GizmoLevel = Exclude<AllGizmoLevel, 0>
export type Energy = typeof ALL_ENERGY_TYPES[number]
export type EnergyWithAny = Energy | 'any'

export enum Stage {
  MAIN = 'MAIN',
  FREE = 'FREE',
  CHOOSE_BUILD = 'CHOOSE_BUILD',
  CHOOSE_FILE = 'CHOOSE_FILE',
  CHOOSE_RESEARCH = 'CHOOSE_RESEARCH',
  RESEARCH = 'RESEARCH',
  PICK = 'PICK',
  DROP = 'DROP',
  GAME_OVER = 'GAME_OVER',
}
