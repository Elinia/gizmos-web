import json
import torch
import copy
from torch.distributions import Categorical

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('../..'))
    from ai_2p.ppo.IDGen import IDGen
    from ai_2p.ppo.PPOModel import PPOModel
    from env.types import ActionType
    from env.common import Stage
    from env.GizmosEnvTraining import GizmosEnvTraining


def sqr(x):
    return x * x


model_name = 'PPO_v2_1'
env = GizmosEnvTraining(player_num=2, model_name=model_name)
idg = IDGen(path='d.json')
models = [PPOModel(idg, path='model/{}-1p.pkl'.format(model_name)),
          PPOModel(idg, path='model/{}-2p.pkl'.format(model_name))]

best_turn: int = 25
best_avg_score: float = 0.0


max_can_num = 0
ppo_actor_loss = 0
ppo_critic_loss = 0
batch_actor_loss = [0.0, 0.0]
batch_other_loss = [0.0, 0.0]
batch_critic_loss = [0.0, 0.0]
batch_count = [0.0, 0.0]

build_num = [0] * 112


try:
    f = open('log/{}-step.log'.format(model_name), 'r')
    start_step = int(f.read()) + 1
except FileNotFoundError:
    start_step = 0

for i in range(start_step, 10000000):
    env.reset()
    last_score = 0
    ret = 0
    input = [[], []]
    output = [[], []]
    ppo_total_loss: list[list[torch.Tensor]] = [[], []]
    traj = []

    last_score = [0, 0]
    while True:
        np = env.state['curr_player_index']
        model = models[np]
        ob = env.observation(np)
        action_space = ob['action_space']
        if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_turn'] > 70:
            break
        act = None
        feature = model.fg.gen_context_feature(ob)
        ti = []
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
            act_feature = model.fg.gen_action_feature(action)
            ti.append(copy.copy(feature + act_feature))
            can_num += 1
        # print("all", can_num)
        max_can_num = max(max_can_num, can_num)
        if can_num == 0:
            act = end_act
            ppo_total_loss[np].append(torch.tensor(0.0))
        else:
            if can_num == 1:
                yhat = model.model.actor_forward(
                    torch.Tensor(ti)).view(-1, )
                ppo_total_loss[np].append(torch.tensor(0.0))
                act = action_space[0]
            else:
                yhat = model.model.actor_forward(
                    torch.Tensor(ti)).view(-1, )
                batch_other_loss[np] += -0.000001 * \
                    torch.sum(torch.log(torch.clamp(yhat, 1e-9, 1.0)))
                best_action = yhat  # / sum(yhat)
                # if i % 100 == 0:
                #     print("!!", best_action, debug)
                # print("?", ti)
                dist = Categorical(best_action)
                idx = dist.sample()
                # print("meet", yhat[idx])
                ppo_total_loss[np].append(yhat[idx] / yhat[idx].detach())
                act = action_space[idx]

        traj.append(str(act))
        act_feature = model.fg.gen_action_feature(act)
        input[np].append(list(map(int, feature + act_feature)))
        # output[np].append((ob['players'][np]['score'] - last_score[np]) / 100.0)
        output[np].append(0)
        last_score[np] = ob['players'][np]['score']
        env.step(np, act)
        if act['type'] in [ActionType.BUILD, ActionType.BUILD_FROM_FILED, ActionType.BUILD_FROM_RESEARCH, ActionType.BUILD_FOR_FREE]:
            build_num[act['id']] += 1

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
        if np == winner:
            if ob['curr_turn'] <= 24:
                multiplier = 24 - ob['curr_turn']
                v = 0.01 * (2 ** multiplier)
        while last >= 0:
            output[np][last] = v
            # v *= 0.999
            last -= 1
    for np in range(2):
        model = models[np]
        vhat = model.model.critic_forward(torch.Tensor(input[np]))
        for j in range(len(input[np]) - 1):
            batch_actor_loss[np] += -ppo_total_loss[np][j] * \
                (output[np][j + 1] - vhat[j].detach())
            batch_critic_loss[np] += sqr(output[np][j] - vhat[j])
        batch_count[np] += len(input[np]) - 1
        if i % 10 == 9:
            loss = (batch_actor_loss[np] * 100 + batch_critic_loss[np] +
                    batch_other_loss[np]) / batch_count[np]
            ppo_actor_loss = batch_actor_loss[np] / batch_count[np]
            ppo_critic_loss = batch_critic_loss[np] / batch_count[np]
            ppo_other_loss = batch_other_loss[np] / batch_count[np]
            batch_actor_loss[np] = 0
            batch_other_loss[np] = 0
            batch_critic_loss[np] = 0
            batch_count[np] = 0
            # loss += 0.00001 * torch.sum(torch.log(torch.clamp(yhat, 1e-9, 1.0)))
            loss.backward()
            # print("?", ppo_total_loss[np][-1], ppo_total_loss[np][-1].grad)
            # print("?", torch.sum(model.base_embedding.grad))
            model.optimizer.step()
            model.optimizer.zero_grad()

    if i == 0:
        continue
    if i % 100 == 0:
        print(traj)
        print("step", i)
    if i % 10 == 0:
        raw_log = "Games played:", i, "; token seen:", idg.cnt, "; loss:", float(ppo_critic_loss), float(ppo_actor_loss), float(ppo_other_loss), "; end turn", ob[
            'curr_turn'], "; final score",  p0['score'],  p1['score'], '; maxcan:', max_can_num
        train_log = ' '.join(map(lambda x: str(x), raw_log))
        print(train_log)
        with open('log/{}.log'.format(model_name), 'a+') as log_file:
            log_file.write(train_log + '\n')

        _raw_log = i, ob['curr_turn'], p0['score'], p1['score']
        _train_log = ','.join([str(x) for x in _raw_log])
        with open('log/{}.csv'.format(model_name), 'a+') as log_file:
            log_file.write(_train_log + '\n')

    if i % 100 == 0:
        for np in range(2):
            model = models[np]
            model.save('model/{}-{}p.pkl'.format(model_name, np + 1))
        with open('log/{}-step.log'.format(model_name), 'w+') as f:
            f.write(str(i))
        res = {}
        for i, num in enumerate(build_num):
            res[str(i)] = num
        js = json.dumps(res)
        with open('r/{}_build_num.json'.format(model_name), 'w+') as f:
            f.write(js)

    if i % 10000 == 0:
        for np in range(2):
            model = models[np]
            model.save('model/{}-{}p{}.pkl'.format(model_name, np + 1, i))

    # print("???", torch.sum(models[1].base_embedding))
    if ob['curr_turn'] < best_turn:
        best_turn = ob['curr_turn']
        env.save_replay('r/PPO_v2_1_replay.json')

    if ob['curr_turn'] == best_turn and (p0['score'] + p1['score']) / ob['curr_turn'] > best_avg_score:
        best_avg_score = (p0['score'] + p1['score']) / ob['curr_turn']
        env.save_replay('r/PPO_v2_1_replay.json')
