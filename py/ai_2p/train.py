import json
import torch
import copy
import random

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from ai_2p.utils import Replay, log_replay
    from ai_2p.IDGen import IDGen
    from ai_2p.QLearner import QLearner
    from env.types import ActionType
    from env.common import Stage
    from env.GizmosEnv import GizmosEnv


env = GizmosEnv(player_num=2, log=False, check=False)

idg = IDGen(path='d.json')
models = [QLearner(idg, path='q_1p.pkl'),
          QLearner(idg, path='q_2p.pkl')]

best_turn: int = 25
best_avg_score: int = 2


log_file = open('q.log', 'a+')

try:
    f = open('q_step.log', 'r')
    start_step = int(f.read()) + 1
except FileNotFoundError:
    start_step = 0

for i in range(start_step, 1000000):
    env.reset()
    input = [[], []]
    output = [[], []]
    traj = []
    replay: Replay = []
    while True:
        np = env.state['curr_player_index']
        model = models[np]
        ob = env.observation(np)
        log_replay(replay, observation=ob)
        action_space = ob['action_space']
        if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_turn'] > 70:
            break
        act = None
        feature = model.fg.gen_context_feature(ob)
        ti = []
        end_act = None
        for action in action_space:
            if action['type'] == ActionType.END:
                end_act = action
                continue
            act_feature = model.fg.gen_action_feature(action)
            ti.append(copy.copy(feature + act_feature))
        yhat = model.model.forward(torch.Tensor(ti)).view(-1,)

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

        traj.append(str(act))
        act_feature = model.fg.gen_action_feature(act)
        input[np].append(list(map(int, feature + act_feature)))
        output[np].append(0)
        env.step(np, act)
        log_replay(replay, action={
                   'name': model.model_name + str(np), 'action': act})

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
        model = models[np]
        input[np] = input[np][:-1]
        output[np] = output[np][1:]
        yhat = model.model.forward(torch.Tensor(input[np]))
        loss = torch.mean(model.model.loss(torch.Tensor(output[np]), yhat))
        model.optimizer.zero_grad()
        loss.backward()
        model.optimizer.step()

    if i == 0:
        continue
    if i % 100 == 0:
        print(traj)
        print("step", i)
    if i % 10 == 0:
        raw_log = "Games played:", i, "; token seen:", idg.cnt, "; loss:", float(loss), "; end turn", ob[
            'curr_turn'], "; final score",  p0['score'],  p1['score']
        train_log = ' '.join(map(lambda x: str(x), raw_log))
        print(train_log)
        log_file.write(train_log + '\n')

    if i % 100 == 0:
        for np in range(2):
            models[np].save('q_{}p.pkl'.format(np + 1))
        with open('q_step.log', 'w+') as f:
            f.write(str(i))

    if i % 10000 == 0:
        for np in range(2):
            models[np].save('q_{}p{}.pkl'.format(np + 1, i))

    if ob['curr_turn'] < best_turn:
        best_turn = ob['curr_turn']
        json_replay = json.dumps(replay)
        with open('q_pro_play.json', 'w+') as f:
            f.write(json_replay)

    if ob['curr_turn'] == best_turn and (p0['score'] + p1['score']) / ob['curr_turn'] > best_avg_score:
        best_avg_score = (p0['score'] + p1['score']) / ob['curr_turn']
        json_replay = json.dumps(replay)
        with open('q_pro_play.json', 'w+') as f:
            f.write(json_replay)
