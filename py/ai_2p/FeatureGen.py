from .utils import lget, lget_id
from .IDGen import IDGen

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import ActionType, Observation, Action


class FeatureGen(object):
    observation_space_len = 68
    action_space_len = 29
    len = observation_space_len + action_space_len

    def __init__(self, idg: IDGen | None = IDGen()):
        self.d: dict[any, int] = {}
        self.cnt = 0
        self.idg = idg

    def gen_context_feature(self, ob: Observation):
        gen = self.idg.gen_unique_id
        np = ob['curr_player_index']
        me = ob['players'][np]
        rival = ob['players'][1 - np]

        board_en = ob['energy_board']
        board_giz = ob['gizmos_board']
        board_giz_l1 = board_giz.get(1) or board_giz.get('1')
        board_giz_l2 = board_giz.get(2) or board_giz.get('2')
        board_giz_l3 = board_giz.get(3) or board_giz.get('3')
        my_en = me['energy_num']
        rival_en = rival['energy_num']
        feature = [
            gen('stage', ob['curr_stage']),
            gen('turn', ob['curr_turn']),
            gen('is_last_turn', ob['is_last_turn']),
            gen('board_red', board_en.count('red')),
            gen('board_black', board_en.count('black')),
            gen('board_blue', board_en.count('blue')),
            gen('board_yellow', board_en.count('yellow')),
            gen('board_giz', lget_id(board_giz_l1, 0)),
            gen('board_giz', lget_id(board_giz_l1, 1)),
            gen('board_giz', lget_id(board_giz_l1, 2)),
            gen('board_giz', lget_id(board_giz_l1, 3)),
            gen('board_giz', lget_id(board_giz_l2, 0)),
            gen('board_giz', lget_id(board_giz_l2, 1)),
            gen('board_giz', lget_id(board_giz_l2, 2)),
            gen('board_giz', lget_id(board_giz_l3, 0)),
            gen('board_giz', lget_id(board_giz_l3, 1)),
            gen('free_pick_num', ob['free_pick_num']),
            gen('free_build', ob['free_build']),
            gen('my_filed', lget_id(me['filed'], 0)),
            gen('my_filed', lget_id(me['filed'], 1)),
            gen('my_filed', lget_id(me['filed'], 2)),
            gen('my_filed', lget_id(me['filed'], 3)),
            gen('my_filed', lget_id(me['filed'], 4)),
            gen('my_giz', lget_id(me['gizmos'], 0)),
            gen('my_giz', lget_id(me['gizmos'], 1)),
            gen('my_giz', lget_id(me['gizmos'], 2)),
            gen('my_giz', lget_id(me['gizmos'], 3)),
            gen('my_giz', lget_id(me['gizmos'], 4)),
            gen('my_giz', lget_id(me['gizmos'], 5)),
            gen('my_giz', lget_id(me['gizmos'], 6)),
            gen('my_giz', lget_id(me['gizmos'], 7)),
            gen('my_giz', lget_id(me['gizmos'], 8)),
            gen('my_giz', lget_id(me['gizmos'], 9)),
            gen('my_giz', lget_id(me['gizmos'], 10)),
            gen('my_giz', lget_id(me['gizmos'], 11)),
            gen('my_giz', lget_id(me['gizmos'], 12)),
            gen('my_giz', lget_id(me['gizmos'], 13)),
            gen('my_giz', lget_id(me['gizmos'], 14)),
            gen('my_giz', lget_id(me['gizmos'], 15)),
            gen('my_red', my_en['red']),
            gen('my_black', my_en['black']),
            gen('my_blue', my_en['blue']),
            gen('my_yellow', my_en['yellow']),
            gen('rival_filed', lget_id(rival['filed'], 0)),
            gen('rival_filed', lget_id(rival['filed'], 1)),
            gen('rival_filed', lget_id(rival['filed'], 2)),
            gen('rival_filed', lget_id(rival['filed'], 3)),
            gen('rival_filed', lget_id(rival['filed'], 4)),
            gen('rival_giz', lget_id(rival['gizmos'], 0)),
            gen('rival_giz', lget_id(rival['gizmos'], 1)),
            gen('rival_giz', lget_id(rival['gizmos'], 2)),
            gen('rival_giz', lget_id(rival['gizmos'], 3)),
            gen('rival_giz', lget_id(rival['gizmos'], 4)),
            gen('rival_giz', lget_id(rival['gizmos'], 5)),
            gen('rival_giz', lget_id(rival['gizmos'], 6)),
            gen('rival_giz', lget_id(rival['gizmos'], 7)),
            gen('rival_giz', lget_id(rival['gizmos'], 8)),
            gen('rival_giz', lget_id(rival['gizmos'], 9)),
            gen('rival_giz', lget_id(rival['gizmos'], 10)),
            gen('rival_giz', lget_id(rival['gizmos'], 11)),
            gen('rival_giz', lget_id(rival['gizmos'], 12)),
            gen('rival_giz', lget_id(rival['gizmos'], 13)),
            gen('rival_giz', lget_id(rival['gizmos'], 14)),
            gen('rival_giz', lget_id(rival['gizmos'], 15)),
            gen('rival_red', rival_en['red']),
            gen('rival_black', rival_en['black']),
            gen('rival_blue', rival_en['blue']),
            gen('rival_yellow', rival_en['yellow']),
        ]
        assert(len(feature) == self.observation_space_len)
        return feature

    def gen_action_feature(self, action: Action):
        feature: list[int] = []
        gen = self.idg.gen_unique_id
        act_type = action['type']
        # feature.append(gen("act_type", act_type))
        if act_type == ActionType.RESEARCH:
            feature.append(gen(act_type, action['level']))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.PICK:
            feature.append(gen(act_type, action['energy']))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.END:
            feature.append(gen(act_type, True))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.GIVE_UP:
            feature.append(gen(act_type, True))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.USE_GIZMO:
            feature.append(gen(act_type, action['id']))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.FILE:
            feature.append(gen(act_type, action['id']))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.FILE_FROM_RESEARCH:
            feature.append(gen(act_type, action['id']))
        else:
            feature.append(gen(act_type))

        if act_type == ActionType.BUILD_FOR_FREE:
            feature.append(gen(act_type, action['id']))
        else:
            feature.append(gen(act_type))

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
            feature.append(gen("cost_giz", lget(cost_giz, 0)))
            feature.append(gen("cost_giz", lget(cost_giz, 1)))
            feature.append(gen("cost_giz", lget(cost_giz, 2)))
            feature.append(gen("cost_giz", lget(cost_giz, 3)))
            feature.append(gen("cost_giz", lget(cost_giz, 4)))
            feature.append(gen("cost_giz", lget(cost_giz, 5)))
            feature.append(gen("cost_giz", lget(cost_giz, 6)))
            feature.append(gen("cost_giz", lget(cost_giz, 7)))
            feature.append(gen("cost_giz", lget(cost_giz, 8)))
            feature.append(gen("cost_giz", lget(cost_giz, 9)))
            feature.append(gen("cost_giz", lget(cost_giz, 10)))
            feature.append(gen("cost_giz", lget(cost_giz, 11)))
            feature.append(gen("cost_giz", lget(cost_giz, 12)))
            feature.append(gen("cost_giz", lget(cost_giz, 13)))
            feature.append(gen("cost_giz", lget(cost_giz, 14)))
            feature.append(gen("cost_giz", lget(cost_giz, 15)))
        else:
            feature.append(gen(act_type))
            feature.append(gen('cost_red'))
            feature.append(gen('cost_black'))
            feature.append(gen('cost_blue'))
            feature.append(gen('cost_yellow'))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))
            feature.append(gen("cost_giz"))

        assert(len(feature) == self.action_space_len)
        return feature
