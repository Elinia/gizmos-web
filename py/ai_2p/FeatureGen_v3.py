from .utils import lget, lget_id
from .IDGen import IDGen

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import ActionType, Observation, Action
    from env.Gizmo import GizmoInfo
    from env.gizmos_pool import gizmos


class FeatureGen(object):
    ob_id_feature_len = 341
    ob_dense_feature_len = 347
    action_id_feature_len = 9
    action_dense_feature_len = 5
    ob_feature_len = ob_id_feature_len + ob_dense_feature_len
    action_feature_len = action_id_feature_len + action_dense_feature_len
    id_feature_len = ob_id_feature_len + action_id_feature_len
    dense_feature_len = ob_dense_feature_len + action_dense_feature_len
    len = id_feature_len + dense_feature_len

    def __init__(self, idg: IDGen | None):
        self.d: dict[any, int] = {}
        self.cnt = 0
        self.idg = idg or IDGen(path='d-v3.json')
        self.gen = self.idg.gen_unique_id

        self.gizmos_id_feature: list[list[int]] = []
        self.gizmos_dense_feature: list[list[int]] = []

    def get_gizmo_id_feature(self, gizmo_id: int | None, prefix=''):
        if gizmo_id is None:
            return [
                self.gen('{}_giz_id'.format(prefix)),
                self.gen('{}_giz_level'.format(prefix)),
                self.gen('{}_giz_energy_type'.format(prefix)),
                self.gen('{}_giz_effect_type'.format(prefix)),
                self.gen('{}_giz_effect_extra_build'.format(prefix))
            ]

        gizmo = gizmos[gizmo_id]

        return [
            self.gen('{}_giz_id'.format(prefix), gizmo.id),
            self.gen('{}_giz_level'.format(prefix), gizmo.level),
            self.gen('{}_giz_energy_type'.format(prefix), gizmo.energy_type),
            self.gen('{}_giz_effect_type'.format(
                prefix), gizmo.effect['type']),
            self.gen('{}_giz_effect_extra_build'.format(prefix),
                     gizmo.effect['type'] == 'extra_build')
        ]

    def get_gizmo_dense_feature(self, gizmo_id: int | None) -> list[int]:
        if gizmo_id is None:
            return [0, 0, 0, 0, 0]

        gizmo = gizmos[gizmo_id]

        return [
            gizmo.energy_cost,
            gizmo.value,
            gizmo.effect['num'] if gizmo.effect['type'] == 'free_draw' else 0,
            gizmo.effect['num'] if gizmo.effect['type'] == 'free_pick' else 0,
            gizmo.effect['num'] if gizmo.effect['type'] == 'add_point_token' else 0,
        ]

    def get_gizmo_state_feature(self, info: GizmoInfo | None, prefix=''):
        if info is None:
            return [
                self.gen('{}_giz_active'.format(prefix)),
                self.gen('{}_giz_used'.format(prefix))
            ]

        return [
            self.gen('{}_giz_active'.format(prefix), info['active']),
            self.gen('{}_giz_used'.format(prefix), info['used'])
        ]

    def get_gizmo_id_feature_with_state(self, info: GizmoInfo | None, prefix=''):
        return self.get_gizmo_id_feature(None if info is None else info['id'], prefix) + self.get_gizmo_state_feature(info)

    def gen_ob_feature(self, ob: Observation):
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
        researching_giz = [] if ob['researching'] is None else ob['researching']['gizmos']
        id_feature = [
            self.gen('np', np),
            self.gen('stage', ob['curr_stage']),
            self.gen('last_turn', ob['is_last_turn']),
            self.gen('free_build', ob['free_build'] is not None),
            *self.get_gizmo_id_feature(lget_id(board_giz_l1, 0), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l1, 1), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l1, 2), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l1, 3), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l2, 0), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l2, 1), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l2, 2), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l3, 0), 'board'),
            *self.get_gizmo_id_feature(lget_id(board_giz_l3, 1), 'board'),
            *self.get_gizmo_id_feature(lget_id(me['filed'], 0), 'me'),
            *self.get_gizmo_id_feature(lget_id(me['filed'], 1), 'me'),
            *self.get_gizmo_id_feature(lget_id(me['filed'], 2), 'me'),
            *self.get_gizmo_id_feature(lget_id(me['filed'], 3), 'me'),
            *self.get_gizmo_id_feature(lget_id(me['filed'], 4), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 0), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 1), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 2), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 3), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 4), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 5), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 6), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 7), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 8), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 9), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 10), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 11), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 12), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 13), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 14), 'me'),
            *self.get_gizmo_id_feature_with_state(lget(me['gizmos'], 15), 'me'),
            *self.get_gizmo_id_feature(lget_id(rival['filed'], 0), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['filed'], 1), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['filed'], 2), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['filed'], 3), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['filed'], 4), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 0), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 1), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 2), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 3), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 4), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 5), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 6), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 7), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 8), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 9), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 10), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 11), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 12), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 13), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 14), 'rival'),
            *self.get_gizmo_id_feature(lget_id(rival['gizmos'], 15), 'rival'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 0), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 1), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 2), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 3), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 4), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 5), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 6), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 7), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 8), 'research'),
            *self.get_gizmo_id_feature(lget_id(researching_giz, 9), 'research'),
        ]
        # print(len(id_feature))
        assert(len(id_feature) == self.ob_id_feature_len)
        dense_feature = [
            ob['curr_turn'],
            board_en.count('red'),
            board_en.count('black'),
            board_en.count('blue'),
            board_en.count('yellow'),
            ob['free_pick_num'],
            my_en['red'],
            my_en['black'],
            my_en['blue'],
            my_en['yellow'],
            me['max_energy_num'],
            me['max_file_num'],
            me['research_num'],
            me['total_energy_num'],
            sum(my_en.values()),
            len(me['gizmos']),
            len(me['level3_gizmos']),
            me['build_from_filed_cost_reduction'],
            me['build_from_research_cost_reduction'],
            len(me['pick_gizmos']),
            len(me['build_gizmos']),
            len(me['converter_gizmos']),
            len(me['file_gizmos']),
            len(me['upgrade_gizmos']),
            rival_en['red'],
            rival_en['black'],
            rival_en['blue'],
            rival_en['yellow'],
            rival['max_energy_num'],
            rival['max_file_num'],
            rival['research_num'],
            rival['total_energy_num'],
            sum(rival_en.values()),
            len(rival['gizmos']),
            len(rival['level3_gizmos']),
            rival['build_from_filed_cost_reduction'],
            rival['build_from_research_cost_reduction'],
            len(rival['pick_gizmos']),
            len(rival['build_gizmos']),
            len(rival['converter_gizmos']),
            len(rival['file_gizmos']),
            len(rival['upgrade_gizmos']),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l1, 0)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l1, 1)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l1, 2)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l1, 3)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l2, 0)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l2, 1)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l2, 2)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l3, 0)),
            *self.get_gizmo_dense_feature(lget_id(board_giz_l3, 1)),
            *self.get_gizmo_dense_feature(lget_id(me['filed'], 0)),
            *self.get_gizmo_dense_feature(lget_id(me['filed'], 1)),
            *self.get_gizmo_dense_feature(lget_id(me['filed'], 2)),
            *self.get_gizmo_dense_feature(lget_id(me['filed'], 3)),
            *self.get_gizmo_dense_feature(lget_id(me['filed'], 4)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 0)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 1)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 2)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 3)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 4)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 5)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 6)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 7)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 8)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 9)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 10)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 11)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 12)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 13)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 14)),
            *self.get_gizmo_dense_feature(lget_id(me['gizmos'], 15)),
            *self.get_gizmo_dense_feature(lget_id(rival['filed'], 0)),
            *self.get_gizmo_dense_feature(lget_id(rival['filed'], 1)),
            *self.get_gizmo_dense_feature(lget_id(rival['filed'], 2)),
            *self.get_gizmo_dense_feature(lget_id(rival['filed'], 3)),
            *self.get_gizmo_dense_feature(lget_id(rival['filed'], 4)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 0)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 1)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 2)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 3)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 4)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 5)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 6)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 7)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 8)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 9)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 10)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 11)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 12)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 13)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 14)),
            *self.get_gizmo_dense_feature(lget_id(rival['gizmos'], 15)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 0)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 1)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 2)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 3)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 4)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 5)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 6)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 7)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 8)),
            *self.get_gizmo_dense_feature(lget_id(researching_giz, 9)),
        ]
        # print(len(dense_feature))
        assert(len(dense_feature) == self.ob_dense_feature_len)
        return id_feature, dense_feature

    def gen_action_feature(self, action: Action):
        id_feature: list[int] = []
        dense_feature: list[int] = []
        gen = self.idg.gen_unique_id
        act_type = action['type']

        if act_type == ActionType.RESEARCH:
            id_feature.append(gen(ActionType.RESEARCH, action['level']))
        else:
            id_feature.append(gen(ActionType.RESEARCH))

        if act_type == ActionType.PICK:
            id_feature.append(gen(ActionType.PICK, action['energy']))
        else:
            id_feature.append(gen(ActionType.PICK))

        if act_type == ActionType.END:
            id_feature.append(gen(ActionType.END, True))
        else:
            id_feature.append(gen(ActionType.END))

        if act_type == ActionType.GIVE_UP:
            id_feature.append(gen(ActionType.GIVE_UP, True))
        else:
            id_feature.append(gen(ActionType.GIVE_UP))

        if act_type == ActionType.USE_GIZMO:
            id_feature.append(gen(ActionType.USE_GIZMO, action['id']))
        else:
            id_feature.append(gen(ActionType.USE_GIZMO))

        if act_type == ActionType.FILE:
            id_feature.append(gen(ActionType.FILE, action['id']))
        else:
            id_feature.append(gen(ActionType.FILE))

        if act_type == ActionType.FILE_FROM_RESEARCH:
            id_feature.append(gen(ActionType.FILE_FROM_RESEARCH, action['id']))
        else:
            id_feature.append(gen(ActionType.FILE_FROM_RESEARCH))

        if act_type == ActionType.BUILD_FOR_FREE:
            id_feature.append(gen(ActionType.BUILD_FOR_FREE, action['id']))
        else:
            id_feature.append(gen(ActionType.BUILD_FOR_FREE))

        if act_type == ActionType.BUILD or \
                act_type == ActionType.BUILD_FROM_FILED or \
                act_type == ActionType.BUILD_FROM_RESEARCH:
            id_feature.append(gen(act_type, action['id']))
            cost_giz = action['cost_converter_gizmos_id']
            dense_feature.append(len(cost_giz))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 0))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 1))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 2))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 3))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 4))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 5))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 6))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 7))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 8))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 9))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 10))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 11))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 12))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 13))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 14))
            # id_feature += self.get_gizmo_id_feature(lget(cost_giz, 15))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 0))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 1))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 2))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 3))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 4))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 5))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 6))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 7))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 8))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 9))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 10))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 11))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 12))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 13))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 14))
            # dense_feature += self.get_gizmo_dense_feature(lget(cost_giz, 15))
            dense_feature.append(action['cost_energy_num']['red'])
            dense_feature.append(action['cost_energy_num']['black'])
            dense_feature.append(action['cost_energy_num']['blue'])
            dense_feature.append(action['cost_energy_num']['yellow'])
        else:
            id_feature.append(gen(ActionType.BUILD))
            dense_feature.append(0)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # id_feature += self.get_gizmo_id_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            # dense_feature += self.get_gizmo_dense_feature(None)
            dense_feature.append(0)
            dense_feature.append(0)
            dense_feature.append(0)
            dense_feature.append(0)

        # print(len(id_feature), len(dense_feature))
        assert(len(id_feature) == self.action_id_feature_len)
        assert(len(dense_feature) == self.action_dense_feature_len)
        return id_feature, dense_feature
