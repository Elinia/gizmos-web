import copy
import torch

from .IDGen import IDGen
from .FeatureGen_v3 import FeatureGen

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import Observation


class Net(torch.nn.Module):
    def __init__(self, fg: FeatureGen, embedding_len: int = 32):
        super(Net, self).__init__()
        self.embedding_len = embedding_len
        self.fg = fg
        self.input_len = self.fg.id_feature_len * \
            self.embedding_len + self.fg.dense_feature_len
        self.base_embedding = torch.nn.Parameter(torch.randn(2000, self.embedding_len),
                                                 requires_grad=True)

        self.loss_op = torch.nn.MSELoss(reduce=False)

        self.model = torch.nn.Sequential(
            torch.nn.Linear(self.input_len, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 1),
        )

    def forward(self, id_feature: torch.Tensor, dense_feature: torch.Tensor) -> torch.Tensor:
        _id_feature = torch.reshape(id_feature, (-1, self.fg.id_feature_len))
        _dense_feature = torch.reshape(
            dense_feature, (-1, self.fg.dense_feature_len))
        ob_id = torch.reshape(
            _id_feature[:, :self.fg.ob_id_feature_len], (-1, 1)).to(torch.long)
        ob_dense = _dense_feature[:, -self.fg.ob_dense_feature_len:]
        action_id = torch.reshape(
            _id_feature[:, :self.fg.action_id_feature_len], (-1, 1)).to(torch.long)
        action_dense = _dense_feature[:, -self.fg.action_dense_feature_len:]
        # print("1", ob_id, ob_dense)
        # print("2", action_id, action_dense)
        batch_input = torch.concat([
            self.base_embedding[ob_id,
                                :].view(-1, self.fg.ob_id_feature_len * self.embedding_len),
            self.base_embedding[action_id, :].view(
                -1, self.fg.action_id_feature_len * self.embedding_len),
            ob_dense,
            action_dense
        ], dim=1)
        return self.model(batch_input)

    def loss(self, y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
        return self.loss_op(yhat.view(-1, ), y.view(-1, ))


class SARSA(torch.nn.Module):
    model_name = "SARSA-v3"

    def __init__(self, idg: IDGen | None, path: str):
        super(SARSA, self).__init__()
        self.idg = idg or IDGen()
        self.fg = FeatureGen(self.idg)

        self.model = Net(self.fg)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.003)

        if not os.path.exists(path):
            print('[{}] init model as {}'.format(path, self.model_name))
        else:
            print('[{}] load model from {}'.format(path, self.model_name))
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    def best_action(self, ob: Observation):
        ob_id, ob_dense = self.fg.gen_ob_feature(ob)
        ti = []
        for action in ob['action_space']:
            action_id, action_dense = self.fg.gen_action_feature(action)
            ti.append(copy.copy(ob_id + ob_dense + action_id + action_dense))
        yhat = self.model.forward(torch.Tensor(ti)).view(-1,)
        return ob['action_space'][torch.argmax(yhat)]

    def save(self, name: str):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, name)
