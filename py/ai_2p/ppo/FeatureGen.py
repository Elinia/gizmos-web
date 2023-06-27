from .IDGen import IDGen

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import ActionType, Observation, Action


class FeatureGen(object):
    observation_space_len = 132
    action_space_len = 14
    len = observation_space_len + action_space_len

    def __init__(self, idg: IDGen | None):
        self.d: dict[any, int] = {}
        self.cnt = 0
        self.idg = idg or IDGen()

    def giz_state(self, np: int, ob: Observation, id: int):
        giz = ob['gizmos'][id]
        belongs_to = 'me' if giz['belongs_to'] == np else 'rival' if giz['belongs_to'] == 1 - np else 'None'
        return '{}_{}_{}_{}_{}'.format(giz['id'], giz['where'], belongs_to, giz['used'], giz['active'])

    def gen_context_feature(self, ob: Observation):
        gen = self.idg.gen_unique_id
        np = ob['curr_player_index']
        me = ob['players'][np]
        rival = ob['players'][1 - np]

        board_en = ob['energy_board']
        my_en = me['energy_num']
        rival_en = rival['energy_num']
        feature = [
            gen('np', np),
            gen('stage', ob['curr_stage']),
            gen('turn', ob['curr_turn']),
            gen('is_last_turn', ob['is_last_turn']),
            gen('board_red', board_en.count('red')),
            gen('board_black', board_en.count('black')),
            gen('board_blue', board_en.count('blue')),
            gen('board_yellow', board_en.count('yellow')),
            gen('free_pick_num', ob['free_pick_num']),
            gen('free_build', ob['free_build']),
            gen('my_red', my_en['red']),
            gen('my_black', my_en['black']),
            gen('my_blue', my_en['blue']),
            gen('my_yellow', my_en['yellow']),
            gen('my_giz_count', len(me['gizmos'])),
            gen('rival_red', rival_en['red']),
            gen('rival_black', rival_en['black']),
            gen('rival_blue', rival_en['blue']),
            gen('rival_yellow', rival_en['yellow']),
            gen('rival_giz_count', len(rival['gizmos'])),
            *[gen('giz', self.giz_state(np, ob, id)) for id in range(112)],
        ]
        assert(len(feature) == self.observation_space_len)
        return feature

    def gen_action_feature(self, action: Action):
        feature: list[int] = []
        gen = self.idg.gen_unique_id
        act_type = action['type']
        # feature.append(gen("act_type", act_type))
        if act_type == ActionType.RESEARCH:
            feature.append(gen(ActionType.RESEARCH, action['level']))
        else:
            feature.append(gen(ActionType.RESEARCH))

        if act_type == ActionType.PICK:
            feature.append(gen(ActionType.PICK, action['energy']))
        else:
            feature.append(gen(ActionType.PICK))

        if act_type == ActionType.END:
            feature.append(gen(ActionType.END, True))
        else:
            feature.append(gen(ActionType.END))

        if act_type == ActionType.GIVE_UP:
            feature.append(gen(ActionType.GIVE_UP, True))
        else:
            feature.append(gen(ActionType.GIVE_UP))

        if act_type == ActionType.USE_GIZMO:
            feature.append(gen(ActionType.USE_GIZMO, action['id']))
        else:
            feature.append(gen(ActionType.USE_GIZMO))

        if act_type == ActionType.FILE:
            feature.append(gen(ActionType.FILE, action['id']))
        else:
            feature.append(gen(ActionType.FILE))

        if act_type == ActionType.FILE_FROM_RESEARCH:
            feature.append(gen(ActionType.FILE_FROM_RESEARCH, action['id']))
        else:
            feature.append(gen(ActionType.FILE_FROM_RESEARCH))

        if act_type == ActionType.BUILD_FOR_FREE:
            feature.append(gen(ActionType.BUILD_FOR_FREE, action['id']))
        else:
            feature.append(gen(ActionType.BUILD_FOR_FREE))

        if act_type == ActionType.BUILD or \
                act_type == ActionType.BUILD_FROM_FILED or \
                act_type == ActionType.BUILD_FROM_RESEARCH:
            feature.append(gen(act_type, action['id']))
            feature.append(gen('cost_red', action['cost_energy_num']['red']))
            feature.append(
                gen('cost_black', action['cost_energy_num']['black']))
            feature.append(gen('cost_blue', action['cost_energy_num']['blue']))
            feature.append(
                gen('cost_yellow', action['cost_energy_num']['yellow']))
            cost_giz = action['cost_converter_gizmos_id']
            feature.append(gen("cost_giz_len", len(cost_giz)))
            # feature.append(gen("cost_giz", lget(cost_giz, 0)))
            # feature.append(gen("cost_giz", lget(cost_giz, 1)))
            # feature.append(gen("cost_giz", lget(cost_giz, 2)))
            # feature.append(gen("cost_giz", lget(cost_giz, 3)))
            # feature.append(gen("cost_giz", lget(cost_giz, 4)))
            # feature.append(gen("cost_giz", lget(cost_giz, 5)))
            # feature.append(gen("cost_giz", lget(cost_giz, 6)))
            # feature.append(gen("cost_giz", lget(cost_giz, 7)))
            # feature.append(gen("cost_giz", lget(cost_giz, 8)))
            # feature.append(gen("cost_giz", lget(cost_giz, 9)))
            # feature.append(gen("cost_giz", lget(cost_giz, 10)))
            # feature.append(gen("cost_giz", lget(cost_giz, 11)))
            # feature.append(gen("cost_giz", lget(cost_giz, 12)))
            # feature.append(gen("cost_giz", lget(cost_giz, 13)))
            # feature.append(gen("cost_giz", lget(cost_giz, 14)))
            # feature.append(gen("cost_giz", lget(cost_giz, 15)))
        else:
            feature.append(gen(ActionType.BUILD))
            feature.append(gen('cost_red'))
            feature.append(gen('cost_black'))
            feature.append(gen('cost_blue'))
            feature.append(gen('cost_yellow'))
            feature.append(gen("cost_giz_len"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))
            # feature.append(gen("cost_giz"))

        assert(len(feature) == self.action_space_len)
        return feature
