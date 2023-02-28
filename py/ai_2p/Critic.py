import copy
from typing import Optional
import torch
from .IDGenerator import IDGenerator

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import ActionType, Observation


class Critic(torch.nn.Module):
    def __init__(self, feature_len: int, idg: Optional[IDGenerator] = None, path='cri.pkl'):
        super(Critic, self).__init__()
        self.idg = idg or IDGenerator()
        self.feature_len = feature_len
        self.embedding_len = 32
        # self.device = 'cpu'
        self.base_embedding = torch.nn.Parameter(torch.randn(10000, self.embedding_len),
                                                 requires_grad=True)

        self.loss_op = torch.nn.MSELoss(reduce=False)

        self.model = torch.nn.Sequential(
            torch.nn.Linear(self.feature_len * self.embedding_len, 1024),
            torch.nn.ReLU(),
            torch.nn.Linear(1024, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 1),
        )

        if not os.path.exists(path):
            print('[Critic.__init__] init model')
        else:
            print('[Critic.__init__] load model from {}'.format(path))
            self.load_state_dict(torch.load(path))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        ids = x.view(-1, 1).to(torch.long)
        batch_input = self.base_embedding[ids,
                                          :].view(-1, self.feature_len * self.embedding_len)
        return self.model(batch_input)

    def best_action(self, ob: Observation):
        feature = self.get_context_feature(ob)
        ti = []
        for j in ob['action_space']:
            self.add_action_feature(feature, j)
            ti.append(copy.copy(feature))
            feature = feature[:-4]
        yhat = self.forward(torch.Tensor(ti)).view(-1,)
        return ob['action_space'][torch.argmax(yhat)]

    def loss(self, y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
        return self.loss_op(y.view(-1, 1), yhat)

    def get_context_feature(self, ob: Observation):
        np = ob['curr_player_index']
        me = ob['players'][np]
        rival = ob['players'][1 - np]
        return [
            self.idg.gen_unique_id('curr_stage', str(ob['curr_stage'])),
            self.idg.gen_unique_id('curr_turn', ob['curr_turn']),
            self.idg.gen_unique_id(
                'energy_board', ob['energy_board'], 0, True),
            self.idg.gen_unique_id(
                'energy_board', ob['energy_board'], 1, True),
            self.idg.gen_unique_id(
                'energy_board', ob['energy_board'], 2, True),
            self.idg.gen_unique_id(
                'energy_board', ob['energy_board'], 3, True),
            self.idg.gen_unique_id(
                'energy_board', ob['energy_board'], 4, True),
            self.idg.gen_unique_id(
                'energy_board', ob['energy_board'], 5, True),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(1, ob['gizmos_board'].get('1')), 0),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(1, ob['gizmos_board'].get('1')), 1),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(1, ob['gizmos_board'].get('1')), 2),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(1, ob['gizmos_board'].get('1')), 3),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(2, ob['gizmos_board'].get('2')), 0),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(2, ob['gizmos_board'].get('2')), 1),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(2, ob['gizmos_board'].get('2')), 2),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(3, ob['gizmos_board'].get('3')), 0),
            self.idg.gen_unique_id(
                'gizmos_board', ob['gizmos_board'].get(3, ob['gizmos_board'].get('3')), 1),
            self.idg.gen_unique_id('free_pick_num', ob['free_pick_num']),
            self.idg.gen_unique_id('players_giz', me['filed'], 0),
            self.idg.gen_unique_id('players_giz', me['filed'], 1),
            self.idg.gen_unique_id('players_giz', me['filed'], 2),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 0),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 1),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 2),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 3),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 4),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 5),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 6),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 7),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 8),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 9),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 10),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 11),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 12),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 13),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 14),
            self.idg.gen_unique_id('players_giz', me['gizmos'], 15),
            self.idg.gen_unique_id('players_giz', rival['filed'], 0),
            self.idg.gen_unique_id('players_giz', rival['filed'], 1),
            self.idg.gen_unique_id('players_giz', rival['filed'], 2),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 0),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 1),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 2),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 3),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 4),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 5),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 6),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 7),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 8),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 9),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 10),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 11),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 12),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 13),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 14),
            self.idg.gen_unique_id('players_giz', rival['gizmos'], 15),
            self.idg.gen_unique_id('ball', me['energy_num']['red']),
            self.idg.gen_unique_id('ball', me['energy_num']['black']),
            self.idg.gen_unique_id('ball', me['energy_num']['blue']),
            self.idg.gen_unique_id('ball', me['energy_num']['yellow']),
            self.idg.gen_unique_id('ball', rival['energy_num']['red']),
            self.idg.gen_unique_id('ball', rival['energy_num']['black']),
            self.idg.gen_unique_id('ball', rival['energy_num']['blue']),
            self.idg.gen_unique_id('ball', rival['energy_num']['yellow'])
        ]

    def add_action_feature(self, feature: list[int], j):
        feature.append(self.idg.gen_unique_id("actiontype", str(j['type'])))
        if j['type'] == ActionType.RESEARCH:
            feature.append(self.idg.gen_unique_id("level", str(j['level'])))
            feature.append(self.idg.gen_unique_id("res", "-1"))
            feature.append(self.idg.gen_unique_id("res", "-1"))
        elif j['type'] == ActionType.PICK:
            feature.append(self.idg.gen_unique_id("energy", str(j['energy'])))
            feature.append(self.idg.gen_unique_id("pic", "-1"))
            feature.append(self.idg.gen_unique_id("pic", "-1"))
        elif j['type'] == ActionType.END:
            feature.append(self.idg.gen_unique_id("en", "-1"))
            feature.append(self.idg.gen_unique_id("en", "-1"))
            feature.append(self.idg.gen_unique_id("en", "-1"))
        elif j['type'] == ActionType.GIVE_UP:
            feature.append(self.idg.gen_unique_id("gi", "-1"))
            feature.append(self.idg.gen_unique_id("gi", "-1"))
            feature.append(self.idg.gen_unique_id("gi", "-1"))
        elif j['type'] == ActionType.USE_GIZMO or j['type'] == ActionType.FILE or j[
                'type'] == ActionType.FILE_FROM_RESEARCH:
            feature.append(self.idg.gen_unique_id("ffr", str(j['id'])))
            feature.append(self.idg.gen_unique_id("ffr", "-1"))
            feature.append(self.idg.gen_unique_id("ffr", "-1"))
        else:
            if 'id' not in j.keys():
                print("??", str(j['type']))
            feature.append(self.idg.gen_unique_id("id", str(j['id'])))
            if j['type'] == ActionType.BUILD_FOR_FREE:
                feature.append(self.idg.gen_unique_id("cos", "-1"))
                feature.append(self.idg.gen_unique_id("ccg", "-1"))
            else:
                feature.append(self.idg.gen_unique_id(
                    "cost", str(j['cost_energy_num'])))
                feature.append(self.idg.gen_unique_id(
                    "cost_converter_gizmos_id", str(len(j['cost_converter_gizmos_id']))))

    def save(self, name='cri.pkl'):
        torch.save(self.state_dict(), name)
