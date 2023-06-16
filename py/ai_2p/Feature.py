# from .utils import lget, lget_id, lget_my_giz
from .IDGen import IDGen

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import ActionType, Observation, Action


class Feature(object):
    ob_id_len = 117
    ob_dense_len = 15
    act_id_len = 9
    act_dense_len = 5
    id_len = ob_id_len + act_id_len
    dense_len = ob_dense_len + act_dense_len
    len = id_len + dense_len

    def __init__(self, idg: IDGen | None):
        self.d: dict[any, int] = {}
        self.cnt = 0
        self.idg: IDGen = idg or IDGen()

    def giz_state(self, np: int, ob: Observation, id: int):
        giz = ob['gizmos'][id]
        belongs_to = 'me' if giz['belongs_to'] == np else 'rival' if giz['belongs_to'] == 1 - np else 'None'
        return '{}_{}_{}_{}_{}'.format(giz['id'], giz['where'], belongs_to, giz['used'], giz['active'])

    def gen_ob_feature(self, ob: Observation):
        gen = self.idg.gen_unique_id
        np = ob['curr_player_index']
        me = ob['players'][np]
        rival = ob['players'][1 - np]

        board_en = ob['energy_board']
        my_en = me['energy_num']
        rival_en = rival['energy_num']
        id_feature = [
            gen('np', np),
            gen('stage', ob['curr_stage']),
            gen('turn', ob['curr_turn']),
            gen('is_last_turn', ob['is_last_turn']),
            gen('free_build', ob['free_build']),
            *[gen('giz', self.giz_state(np, ob, id)) for id in range(112)],
        ]
        assert(len(id_feature) == self.ob_id_len)
        dense_feature = [
            board_en.count('red'),
            board_en.count('black'),
            board_en.count('blue'),
            board_en.count('yellow'),
            ob['free_pick_num'],
            my_en['red'],
            my_en['black'],
            my_en['blue'],
            my_en['yellow'],
            len(me['gizmos']),
            rival_en['red'],
            rival_en['black'],
            rival_en['blue'],
            rival_en['yellow'],
            len(rival['gizmos']),
        ]
        assert(len(dense_feature) == self.ob_dense_len)
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
            dense_feature.append(action['cost_energy_num']['red'])
            dense_feature.append(action['cost_energy_num']['black'])
            dense_feature.append(action['cost_energy_num']['blue'])
            dense_feature.append(action['cost_energy_num']['yellow'])
            cost_giz = action['cost_converter_gizmos_id']
            dense_feature.append(len(cost_giz))
        else:
            id_feature.append(gen(ActionType.BUILD))
            dense_feature.append(0)
            dense_feature.append(0)
            dense_feature.append(0)
            dense_feature.append(0)
            dense_feature.append(0)

        assert(len(id_feature) == self.act_id_len)
        assert(len(dense_feature) == self.act_dense_len)
        return id_feature, dense_feature
