import copy
import numpy as np
import torch
from torch import Tensor
import torch.nn as nn
import torch.nn.functional as F
from itertools import chain
from .Feature import Feature

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ReplayBuffer(object):
    def __init__(self, max_size=int(1e5)):
        self.max_size = max_size
        self.ptr = [0, 0]
        self.size = [0, 0]

        self.ids = [np.zeros((max_size, Feature.id_len)),
                    np.zeros((max_size, Feature.id_len))]
        self.ds = [np.zeros((max_size, Feature.dense_len)),
                   np.zeros((max_size, Feature.dense_len))]
        self.next_ids = [np.zeros((max_size, Feature.id_len)), np.zeros(
            (max_size, Feature.id_len))]
        self.next_ds = [np.zeros((max_size, Feature.dense_len)), np.zeros(
            (max_size, Feature.dense_len))]
        self.reward = [np.zeros((max_size, 1)), np.zeros((max_size, 1))]
        self.done = [np.zeros((max_size, 1)), np.zeros((max_size, 1))]

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

    def add(self, nowp, ids, ds, next_ids, next_ds, reward, done):
        self.ids[nowp][self.ptr[nowp]] = ids
        self.ds[nowp][self.ptr[nowp]] = ds
        self.next_ids[nowp][self.ptr[nowp]] = next_ids
        self.next_ds[nowp][self.ptr[nowp]] = next_ds
        self.reward[nowp][self.ptr[nowp]] = reward
        self.done[nowp][self.ptr[nowp]] = done

        self.ptr[nowp] = (self.ptr[nowp] + 1) % self.max_size
        self.size[nowp] = min(self.size[nowp] + 1, self.max_size)

    def sample(self, nowp, batch_size):
        ind = np.random.randint(0, self.size[nowp], size=batch_size)

        return (
            torch.FloatTensor(self.ids[nowp][ind]).to(self.device),
            torch.FloatTensor(self.ds[nowp][ind]).to(self.device),
            torch.FloatTensor(self.next_ids[nowp][ind]).to(self.device),
            torch.FloatTensor(self.next_ds[nowp][ind]).to(self.device),
            torch.FloatTensor(self.reward[nowp][ind]).to(self.device),
            torch.FloatTensor(self.done[nowp][ind]).to(self.device),
        )


class SharedEmbedding(nn.Module):
    def __init__(self):
        super(SharedEmbedding, self).__init__()
        self.embedding_len = 8
        self.base_embedding = torch.nn.Parameter(
            torch.randn(2000, self.embedding_len), requires_grad=True)

    def embedding_look_up(self, ids):
        return self.base_embedding[ids, :]


class CriticA(nn.Module):
    def __init__(self):
        super(CriticA, self).__init__()
        self.model_name = "TD3_CA"

        self.embedding_len = 8
        self.input_len = Feature.id_len * self.embedding_len + Feature.dense_len

        # Q1 architecture
        self.l1 = nn.Linear(self.input_len, 256)
        self.l2 = nn.Linear(256, 256)
        self.l3 = nn.Linear(256, 1)

        # Q2 architecture
        self.l4 = nn.Linear(self.input_len, 256)
        self.l5 = nn.Linear(256, 256)
        self.l6 = nn.Linear(256, 1)

    def forward(self, state: Tensor, action: Tensor):
        sa = torch.cat([state, action], 1)

        a1 = F.relu(self.l1(sa))
        a1 = F.relu(self.l2(a1))
        a1 = self.l3(a1)

        a2 = F.relu(self.l4(sa))
        a2 = F.relu(self.l5(a2))
        a2 = self.l6(a2)
        return a1, a2

    def A1(self, state: Tensor, action: Tensor):
        sa = torch.cat([state, action], 1)

        a1 = F.relu(self.l1(sa))
        a1 = F.relu(self.l2(a1))
        a1 = self.l3(a1)
        return a1


class CriticV(nn.Module):
    def __init__(self):
        super(CriticV, self).__init__()
        self.model_name = "TD3_CQ"

        self.embedding_len = 8
        self.input_len = Feature.ob_id_len * self.embedding_len + Feature.ob_dense_len

        # V1 architecture
        self.l1 = nn.Linear(self.input_len, 256)
        self.l2 = nn.Linear(256, 256)
        self.l3 = nn.Linear(256, 1)

        # V2 architecture
        self.l4 = nn.Linear(self.input_len, 256)
        self.l5 = nn.Linear(256, 256)
        self.l6 = nn.Linear(256, 1)

    def forward(self, state):
        s = torch.cat([state, ], 1)

        v1 = F.relu(self.l1(s))
        v1 = F.relu(self.l2(v1))
        v1 = self.l3(v1)

        v2 = F.relu(self.l4(s))
        v2 = F.relu(self.l5(v2))
        v2 = self.l6(v2)
        return v1, v2

    def V1(self, state):
        s = torch.cat([state, ], 1)

        v1 = F.relu(self.l1(s))
        v1 = F.relu(self.l2(v1))
        v1 = self.l3(v1)
        return v1


class TD3(Feature):
    def __init__(
            self,
            idg,
            discount=0.99,
            tau=0.005,
            policy_noise=0.2,
            noise_clip=0.5,
            policy_freq=8
    ):
        self.model_name = "TD3"
        self.idg = idg
        super().__init__(idg)
        self.embedding_table = SharedEmbedding()
        self.criticA = CriticA().to(device)
        # self.criticQ = CriticQ().to(device)
        # self.criticQ_target = copy.deepcopy(self.criticQ)
        # self.criticQ_optimizer = torch.optim.Adam(self.criticQ.parameters(), lr=3e-4)

        self.criticV = CriticV().to(device)
        self.criticV_target = copy.deepcopy(self.criticV)
        self.optimizer = torch.optim.Adam(
            set(chain(self.criticA.parameters(), self.criticV.parameters())), lr=3e-4)

        self.discount = discount
        self.tau = tau
        self.policy_noise = policy_noise
        self.noise_clip = noise_clip
        self.policy_freq = policy_freq

        self.total_it = 0

    def forward(self, id_feature: Tensor, dense_feature: Tensor):
        # print(id_feature.shape, dense_feature.shape)
        with torch.no_grad():
            _id_feature = torch.reshape(id_feature, (-1, Feature.id_len))
            _dense_feature = torch.reshape(
                dense_feature, (-1, Feature.dense_len))
            ob_id = torch.reshape(
                _id_feature[:, :Feature.ob_id_len], (-1, 1)).to(torch.long)
            ob_dense = _dense_feature[:, -Feature.ob_dense_len:]
            action_id = torch.reshape(
                _id_feature[:, :Feature.act_id_len], (-1, 1)).to(torch.long)
            action_dense = _dense_feature[:, -Feature.act_dense_len:]
            # print("1", ob_id, ob_dense)
            # print("2", action_id, action_dense)
            batch_state = torch.concat([
                self.embedding_table.embedding_look_up(
                    ob_id).view(-1, Feature.ob_id_len * self.embedding_table.embedding_len),
                ob_dense], dim=1)
            batch_action = torch.concat([
                self.embedding_table.embedding_look_up(action_id).view(
                    -1, Feature.act_id_len * self.embedding_table.embedding_len),
                action_dense
            ], dim=1)
            # print(batch_state.shape, batch_action.shape)

            A = self.criticA.A1(batch_state, batch_action)
            # if random.random() < 0.1:
            action = (A + np.random.normal(0, 0.001, size=A.shape))
            # else:
            #     action = Q
            # print(Q.shape, action.shape)
            return action

        # state = torch.FloatTensor(state.reshape(1, -1)).to(device)
        # return self.actor(state).cpu().data.numpy().flatten()

    def train(self, nowp, replay_buffer: ReplayBuffer, batch_size=256):
        self.total_it += 1
        # Sample replay buffer
        ids, ds, next_ids, next_ds, reward, done = replay_buffer.sample(
            nowp, batch_size)
        _id_feature = torch.reshape(ids, (-1, Feature.id_len))
        _dense_feature = torch.reshape(ds, (-1, Feature.dense_len))
        ob_id = torch.reshape(
            _id_feature[:, :Feature.ob_id_len], (-1, 1)).to(torch.long)
        ob_dense = _dense_feature[:, -Feature.ob_dense_len:]
        action_id = torch.reshape(
            _id_feature[:, :Feature.act_id_len], (-1, 1)).to(torch.long)
        action_dense = _dense_feature[:, -Feature.act_dense_len:]
        state = torch.concat([self.embedding_table.embedding_look_up(
            ob_id).view(-1, Feature.ob_id_len * self.embedding_table.embedding_len), ob_dense], dim=1)
        action = torch.concat([self.embedding_table.embedding_look_up(
            action_id).view(-1, Feature.act_id_len * self.embedding_table.embedding_len), action_dense], dim=1)
        with torch.no_grad():
            _id_feature = torch.reshape(next_ids, (-1, Feature.id_len))
            _dense_feature = torch.reshape(next_ds, (-1, Feature.dense_len))
            ob_id = torch.reshape(
                _id_feature[:, :Feature.ob_id_len], (-1, 1)).to(torch.long)
            ob_dense = _dense_feature[:, -Feature.ob_dense_len:]
            next_state = torch.concat([self.embedding_table.embedding_look_up(ob_id).view(-1,
                                                                                          Feature.ob_id_len * self.embedding_table.embedding_len), ob_dense], dim=1)
            # Compute the target Q value
            target_V1, target_V2 = self.criticV_target(next_state)
            target_V = torch.min(target_V1, target_V2)
            target_V = reward + done * self.discount * target_V

        # Get current Q estimates
        current_A1, current_A2 = self.criticA(state, action)
        current_V1, current_V2 = self.criticV(state)
        # Compute critic loss
        critic_loss = F.mse_loss(
            current_A1 + current_V1, target_V) + F.mse_loss(current_A2 + current_V2, target_V)

        # Optimize the critic
        self.optimizer.zero_grad()
        critic_loss.backward()
        # print(torch.sum(torch.abs(self.embedding_table.base_embedding.grad)), "?")
        self.optimizer.step()

        # Delayed policy updates
        if self.total_it % self.policy_freq == 0:
            # Update the frozen target models
            # for param, target_param in zip(self.criticQ.parameters(), self.criticQ_target.parameters()):
            #     target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
            for param, target_param in zip(self.criticV.parameters(), self.criticV_target.parameters()):
                target_param.data.copy_(
                    self.tau * param.data + (1 - self.tau) * target_param.data)
