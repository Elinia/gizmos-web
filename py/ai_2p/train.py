import json
import torch
import copy
import random

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from ai_2p.IDGenerator import IDGenerator
    from ai_2p.Critic import Critic
    from env.types import ActionType, Observation, Action
    from env.common import Stage
    from env.GizmosEnv import GizmosEnv


env = GizmosEnv(player_num=2, log=False, check=False)
debug_round = 1000

idg = IDGenerator(path='d.json')
critics = [Critic(64 + 4, idg, path='cri-1p.pkl'),
           Critic(64 + 4, idg, path='cri-2p.pkl')]
optimizers = [torch.optim.SGD(critic.parameters(), lr=0.01)
              for critic in critics]
# optimizers = torch.optim.Adam(critic.parameters(), lr=0.01)
# optimizers = torch.optim.RMSprop(critic.parameters())

best_turn: int = 25


def log_replay(replay: list[Observation | Action],
               observation: Observation | None = None,
               action: Action | None = None):
    if observation == None:
        if action == None:
            return
        replay.append(copy.deepcopy(action))
    else:
        ob = copy.deepcopy(observation)
        del ob['gizmos']
        replay.append(ob)


for i in range(1000000):
    env.reset()
    last_score = 0
    ret = 0
    input = [[], []]
    output = [[], []]
    action = [[], []]
    traj = []
    replay: list[Observation | Action] = []
    while True:
        np = env.state['curr_player_index']
        ob = env.observation(np)
        log_replay(replay, observation=ob)
        action_space = ob['action_space']
        if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_turn'] > 70:
            break
        act = None
        feature = critics[0].get_context_feature(ob)
        ti = []
        end_act = None
        for j in action_space:
            if j['type'] == ActionType.END:
                end_act = j
                continue
            critics[0].add_action_feature(feature, j)
            ti.append(copy.copy(feature))
            feature = feature[:-4]
        tmp = torch.Tensor(ti)
        yhat = critics[np].forward(torch.Tensor(ti)).view(-1,)

        def sample_gumbel(shape, eps=1e-20):
            U = torch.rand(shape)
            return -torch.log(-torch.log(U + eps) + eps)
        if random.random() < 0.05:
            best_action = sample_gumbel(yhat.shape) / 1.0
        else:
            best_action = yhat  # + sample_gumbel(yhat.shape) / 10000.0
        # print(yhat, best_action)
        if best_action.numel() == 0:
            act = end_act
        else:
            act = action_space[torch.argmax(best_action)]
        critics[0].add_action_feature(feature, act)

        traj.append(str(act))
        # feature.append(self.idg.gen_unique_id("action", str(act)))
        input[np].append(list(map(int, feature)))
        output[np].append(0)
        env.step(np, act)
        log_replay(replay, action=act)

    ob = env.observation(0)
    p0 = ob['players'][0]
    p1 = ob['players'][1]
    if p0['score'] != p1['score']:
        winner = 0 if p0['score'] > p1['score'] else 1
    elif len(p0['gizmos']) != len(p1['gizmos']):
        winner = 0 if len(p0['gizmos']) > len(p1['gizmos']) else 1
    elif p0['total_energy_num'] != p1['total_energy_num']:
        winner = 0 if p0['total_energy_num'] > p1['total_energy_num'] else 1
    else:
        winner = 1

    for np in range(2):
        last = len(output[np]) - 1
        v = 0 + ob['players'][np]['score'] / 100.0
        if np == winner:
            v += 1
        while last >= 0:
            output[np][last] = v
            last -= 1
    for np in range(2):
        input[np] = input[np][:-1]
        output[np] = output[np][1:]
        yhat = critics[np].forward(torch.Tensor(input[np]))
        loss = torch.mean(critics[np].loss(torch.Tensor(output[np]), yhat))
        optimizers[np].zero_grad()
        loss.backward()
        optimizers[np].step()

    if i == 0:
        continue
    if i % debug_round == 0:
        print(traj)
        print("step", i)
    if i % 10 == 0:
        print("Games played:", i, "; token seen:", idg.cnt, "; loss:", float(loss), "; end turn", ob[
              'curr_turn'], "; final score",  p0['score'],  p1['score'])

    if i % 100 == 0:
        for np in range(2):
            critics[np].save('cri-{}p.pkl'.format(np + 1))

    if ob['curr_turn'] < best_turn:
        best_turn = ob['curr_turn']
        json_replay = json.dumps(replay)
        with open('pro_play.json', 'w+') as f:
            f.write(json_replay)
