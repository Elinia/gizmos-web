import copy
import torch

from .IDGen import IDGen
from .FeatureGen import FeatureGen

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('../..'))
    from env.types import Observation


class Net(torch.nn.Module):
    def __init__(self, actor_feature_len: int, critic_feature_len: int, embedding_len: int = 64):
        super(Net, self).__init__()
        self.actor_feature_len = actor_feature_len
        self.critic_feature_len = critic_feature_len
        self.embedding_len = embedding_len
        self.base_embedding = torch.nn.Parameter(torch.randn(10000, self.embedding_len) / 10.0,
                                                 requires_grad=True)

        self.critic_loss_op = torch.nn.MSELoss(reduce=False)

        self.actor_model = torch.nn.Sequential(
            torch.nn.Linear(self.actor_feature_len * self.embedding_len, 512),
            torch.nn.Tanh(),
            # torch.nn.Linear(512, 512),
            # torch.nn.Tanh(),
            # torch.nn.Linear(512, 512),
            # torch.nn.Tanh(),
            # torch.nn.Linear(1024, 512),
            # torch.nn.ReLU(),
            # torch.nn.Linear(512, 256),
            # torch.nn.ReLU(),
            # torch.nn.Linear(256, 128),
            # torch.nn.ReLU(),
            # torch.nn.Linear(128, 64),
            # torch.nn.ReLU(),
            torch.nn.Linear(512, 1),
            torch.nn.Softmax(dim=0)
        )

        self.critic_model = torch.nn.Sequential(
            torch.nn.Linear(self.critic_feature_len * self.embedding_len, 512),
            torch.nn.ReLU(),
            # torch.nn.Linear(512, 512),
            # torch.nn.ReLU(),
            # torch.nn.Linear(512, 512),
            # torch.nn.ReLU(),
            # torch.nn.Linear(1024, 512),
            # torch.nn.ReLU(),
            # torch.nn.Linear(512, 256),
            # torch.nn.ReLU(),
            # torch.nn.Linear(256, 128),
            # torch.nn.ReLU(),
            # torch.nn.Linear(128, 64),
            # torch.nn.ReLU(),
            torch.nn.Linear(512, 1),
            # torch.nn.Sigmoid()
            # torch.nn.Sigmoid()
        )

    def actor_forward(self, x: torch.Tensor) -> torch.Tensor:
        ids = x.view(-1, 1).to(torch.long)
        batch_input = self.base_embedding[ids,
                                          :].view(-1, self.actor_feature_len * self.embedding_len)
        return self.actor_model(batch_input)

    def critic_forward(self, x: torch.Tensor) -> torch.Tensor:
        ids = x.view(-1, 1).to(torch.long)
        batch_input = self.base_embedding[ids,
                                          :].view(-1, self.actor_feature_len * self.embedding_len)
        return self.critic_model(batch_input[:, :-(self.actor_feature_len - self.critic_feature_len)*self.embedding_len])

    def critic_loss(self, y: torch.Tensor, yhat: torch.Tensor) -> torch.Tensor:
        return self.critic_loss_op(yhat, y.view(-1, 1))


class PPOModel(torch.nn.Module):
    model_name = "PPO"

    def __init__(self, idg: IDGen | None, path='ppo.pkl'):
        super(PPOModel, self).__init__()
        self.idg = idg or IDGen()
        self.fg = FeatureGen(self.idg)

        self.model = Net(self.fg.len,
                         self.fg.observation_space_len)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.003)

        if not os.path.exists(path):
            print('[PPOModel.__init__] init model as {}'.format(path))
        else:
            print('[PPOModel.__init__] load model from {}'.format(path))
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    def best_action(self, ob: Observation):
        feature = self.fg.gen_context_feature(ob)
        ti = []
        for action in ob['action_space']:
            action_feature = self.fg.gen_action_feature(action)
            ti.append(copy.copy(feature + action_feature))
        yhat = self.model.actor_forward(torch.Tensor(ti)).view(-1,)
        return ob['action_space'][torch.argmax(yhat)]

    def save(self, name='ppo.pkl'):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, name)
