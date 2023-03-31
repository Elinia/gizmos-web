import json
import torch
import copy
import random

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from ai_2p.IDGen import IDGen
    from ai_2p.SARSA_v3 import SARSA
    from env.types import ActionType
    from env.common import Stage
    from env.GizmosEnvTraining import GizmosEnvTraining


def sqr(x):
    return x * x


model_name = 'SARSA-v3'
env = GizmosEnvTraining(player_num=2, model_name=model_name)
idg = IDGen(path='d-v3.json')
models = [SARSA(idg, path='{}-1p.pkl'.format(model_name)),
          SARSA(idg, path='{}-2p.pkl'.format(model_name))]

best_turn: int = 20
best_avg_score: float = 0.0

max_turn = 25

max_can_num = 0
ppo_actor_loss = 0
ppo_critic_loss = 0
batch_actor_loss = [0.0, 0.0]
batch_other_loss = [0.0, 0.0]
batch_critic_loss = [0.0, 0.0]
batch_count = [0.0, 0.0]


try:
    f = open('{}-step.log'.format(model_name), 'r')
    start_step = int(f.read()) + 1
except FileNotFoundError:
    start_step = 0

for i in range(start_step, 10000000):
    env.reset()
    last_score = 0
    ret = 0
    input = [[], []]
    input_dense = [[], []]
    output: list[list[float]] = [[], []]
    ppo_total_loss: list[list[torch.Tensor]] = [[], []]
    random_a = [[], []]
    action = [[], []]
    traj = []

    last_score = [0, 0]
    last_ball_num = [0, 0]
    while True:
        np = env.state['curr_player_index']
        model = models[np]
        ob = env.observation(np)
        me = ob['players'][np]
        curr_turn = ob['curr_turn']
        action_space = ob['action_space']
        if ob['curr_stage'] == Stage.GAME_OVER or curr_turn > max_turn:
            break
        act = None
        ob_id, ob_dense = model.fg.gen_ob_feature(ob)
        ti_id = []
        ti_dense = []
        end_act = None
        can_num = 0
        debug = []

        for action in action_space:
            if action['type'] == ActionType.END:
                end_act = action
                # print("end", can_num)
                continue
            ids = "None"
            if "id" in action.keys():
                ids = action['id']
            debug.append(action['type'] + str(ids))
            act_id, act_dense = model.fg.gen_action_feature(action)
            ti_id.append(copy.copy(ob_id + act_id))
            ti_dense.append(copy.copy(ob_dense + act_dense))
            can_num += 1
        # print("all", can_num)
        max_can_num = max(max_can_num, can_num)

        yhat = model.model.forward(torch.Tensor(
            ti_id), torch.Tensor(ti_dense)).view(-1,)
        # def sample_gumbel(shape, eps=1e-20):
        #     U = torch.rand(shape)
        #     return -torch.log(-torch.log(U + eps) + eps)
        if random.random() < 0.05:
            best_action = torch.rand(yhat.shape) / 1.0
            random_a[np].append(True)
        else:
            best_action = yhat  # + sample_gumbel(yhat.shape) / 10000.0
            random_a[np].append(False)
        # print(yhat, best_action)
        if best_action.numel() == 0:
            act = end_act
            random_a[np][-1] = False
        else:
            idx = torch.argmax(best_action)
            act = action_space[idx]

        traj.append(str(curr_turn) + ": " + str(act))
        act_id, act_dense = model.fg.gen_action_feature(act)
        input[np].append(list(map(int, ob_id + act_id)))
        input_dense[np].append(list(map(float, ob_dense + act_dense)))
        # print(ob_dense + act_dense)

        # score_reward = (me['score'] - last_score[np]) / 100.0
        # ball_reward = (me['total_energy_num'] -
        #                last_ball_num[np]) / 1000.0

        # output[np].append(score_reward + ball_reward)
        output[np].append(0)
        last_score[np] = me['score']
        last_ball_num[np] = me['total_energy_num']
        env.step(np, act)

    ob = env.observation(0)
    p0 = ob['players'][0]
    p1 = ob['players'][1]
    for np in range(2):
        me = ob['players'][np]
        rival = ob['players'][1-np]
        reward = env.get_reward(np)
        turn_reward = float((max_turn + 2 - ob['curr_turn']) * reward)
        score_reward = (me['score'] - rival['score']) / 100.0
        output[np].append(turn_reward + score_reward)
    for np in range(2):
        model = models[np]
        yhat = model.model.forward(torch.Tensor(
            input[np]), torch.Tensor(input_dense[np]))
        for j in range(len(input[np])):
            if j == len(input[np]) - 1:
                batch_critic_loss[np] += sqr(output[np][j + 1] - yhat[j])
            else:
                if not random_a[np][j + 1]:
                    batch_critic_loss[np] += sqr(
                        yhat[j + 1].detach() - yhat[j] - output[np][j + 1])
                else:
                    batch_count[np] -= 1
        batch_count[np] += len(input[np])
        if batch_count[np] > 0:
            loss = batch_critic_loss[np] / batch_count[np]
            loss.backward()
            model.optimizer.step()
            model.optimizer.zero_grad()
            batch_critic_loss[np] = 0
            batch_count[np] = 0
            qlloss = loss

    if i == 0:
        continue
    if i % 100 == 0:
        print(traj)
        print("step", i)
    if i % 10 == 0:
        raw_log = "Games played:", i, "; token seen:", idg.cnt, "; loss:", float(qlloss), "; end turn", ob[
            'curr_turn'], "; final score",  p0['score'],  p1['score'], '; maxcan:', max_can_num

        train_log = ' '.join(map(lambda x: str(x), raw_log))
        print(train_log)
        with open('{}.log'.format(model_name), 'a+') as log_file:
            log_file.write(train_log + '\n')

        _raw_log = i, ob['curr_turn'], p0['score'], p1['score']
        _train_log = ','.join([str(x) for x in _raw_log])
        with open('{}.csv'.format(model_name), 'a+') as log_file:
            log_file.write(_train_log + '\n')

    if i % 100 == 0:
        for np in range(2):
            model = models[np]
            model.save('{}-{}p.pkl'.format(model_name, np + 1))
        with open('{}-step.log'.format(model_name), 'w+') as f:
            f.write(str(i))

    if i % 10000 == 0:
        for np in range(2):
            model = models[np]
            model.save('{}-{}p{}.pkl'.format(model_name, np + 1, i))

    replay_path = '{}_pro_play.json'.format(model_name)

    if ob['curr_turn'] < best_turn:
        best_turn = ob['curr_turn']
        env.save_replay(replay_path)

    if ob['curr_turn'] == best_turn and (p0['score'] + p1['score']) / ob['curr_turn'] > best_avg_score:
        best_avg_score = (p0['score'] + p1['score']) / ob['curr_turn']
        env.save_replay(replay_path)
