import json
from typing import TypeGuard
import torch
import copy
import random
from torch.distributions import Categorical
# import visdom

# vis = visdom.Visdom(env='giz')
first = True
total_round = 0
total_score = [0, 0]
if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from ai_2p.utils import Replay, log_replay
    from ai_2p.IDGen import IDGen
    from ai_2p.PPOModel import PPOModel
    from ai_2p.QLearner import QLearner
    from env.types import ActionType
    from env.common import Stage
    from env.GizmosEnv import GizmosEnv


def sqr(x):
    return x * x


env = GizmosEnv(player_num=2, log=False, check=False)

idg = IDGen(path='d.json')
models = [PPOModel(idg, path='ppo-1p.pkl'), PPOModel(idg, path='ppo-2p.pkl')]

best_turn: int = 25
best_avg_score: float = 0.0


log_file = open('PPO.log', 'a+')

w0 = 0
w1 = 0
max_can_num = 0
ppo_actor_loss = 0
ppo_critic_loss = 0
batch_actor_loss = [0.0, 0.0]
batch_other_loss = [0.0, 0.0]
batch_critic_loss = [0.0, 0.0]
batch_count = [0.0, 0.0]


def is_q_learner(model: PPOModel | QLearner) -> TypeGuard[QLearner]:
    return model.model_name == 'QLearner'


def is_ppo(model: PPOModel | QLearner) -> TypeGuard[PPOModel]:
    return model.model_name == 'PPO'


try:
    f = open('PPO-step.log', 'r')
    start_step = int(f.read()) + 1
except FileNotFoundError:
    start_step = 0

for i in range(start_step, 1000000):
    env.reset()
    last_score = 0
    ret = 0
    input = [[], []]
    output = [[], []]
    ppo_total_loss: list[list[torch.Tensor]] = [[], []]
    traj = []
    replay: Replay = []

    last_score = [0, 0]
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
        if is_ppo(model):
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
                    if i % 100 == 0:
                        print("!!", best_action, debug)
                    # print("?", ti)
                    dist = Categorical(best_action)
                    idx = dist.sample()
                    # print("meet", yhat[idx])
                    ppo_total_loss[np].append(yhat[idx] / yhat[idx].detach())
                    act = action_space[idx]

        elif is_q_learner(model):
            yhat = model.model.forward(torch.Tensor(ti)).view(-1,)
            # def sample_gumbel(shape, eps=1e-20):
            #     U = torch.rand(shape)
            #     return -torch.log(-torch.log(U + eps) + eps)
            if random.random() < 0.05:
                best_action = torch.rand(yhat.shape) / 1.0
            else:
                best_action = yhat  # + sample_gumbel(yhat.shape) / 10000.0
            # print(yhat, best_action)
            if best_action.numel() == 0:
                act = end_act
            else:
                idx = torch.argmax(best_action)
                act = action_space[idx]
        else:
            print("incomplete model")
            exit(0)

        traj.append(str(act))
        act_feature = model.fg.gen_action_feature(act)
        input[np].append(list(map(int, feature + act_feature)))
        # output[np].append((ob['players'][np]['score'] - last_score[np]) / 100.0)
        output[np].append(0)
        last_score[np] = ob['players'][np]['score']
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
    if winner == 0:
        w0 += 1
    else:
        w1 += 1
    total_round += ob['curr_turn']
    total_score[0] += ob['players'][0]['score']
    total_score[1] += ob['players'][1]['score']
    for np in range(2):
        last = len(output[np]) - 1
        v = 0 + (ob['players'][np]['score']) / 1000.0
        v = 0  # - ob[
        # 'curr_turn'] * 10) / 100.0
        if np == winner:
            # v += ob['players'][np]['score'] / ob['curr_turn']
            v += 1
        while last >= 0:
            output[np][last] = v
            # v *= 0.999
            last -= 1
    for np in range(2):
        # input[np] = input[np][:-1]
        # output[np] = output[np][1:]
        model = models[np]
        if is_ppo(model):
            # model.optimizer.zero_grad()
            vhat = model.model.critic_forward(torch.Tensor(input[np]))
            for j in range(len(input[np]) - 1):
                batch_actor_loss[np] += -ppo_total_loss[np][j] * \
                    (output[np][j + 1] - vhat[j].detach())
                # append(output[np][j])
                batch_critic_loss[np] += sqr(output[np][j] - vhat[j])
                # batch_critic_loss_vhat[np].append(vhat[j])
            batch_count[np] += len(input[np]) - 1
            # batch_out[np] += output[np][1:]
            # batch_out_all[np] += output[np]
            # batch_ppo_total_loss[np] += ppo_total_loss[np][:-1]
            if i % 10 == 9:
                # yhat = model.actor_forward(torch.Tensor(input[np][:-1]))
                # print("!!!", ppo_total_loss[np][:-1])
                # print(ppo_total_loss[np][:-1])
                # print((torch.Tensor(output[np][1:]) - vhat[:-1].detach()))
                # A = torch.stack(batch_ppo_total_loss[np]) * (torch.Tensor(batch_out[np]) - vhat[:-1].detach())
                # A = torch.log(yhat / torch.sum(yhat.detach())) * (torch.Tensor(output[np][1:]))
                # ppo_actor_loss = -torch.mean(torch.stack) * 3
                # ppo_actor_loss = torch.sum(ppo_total_loss[np][:-1])
                # ppo_critic_loss = torch.mean(model.critic_loss(torch.Tensor(output[np]), vhat))
                # loss = ppo_actor_loss + ppo_critic_loss

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
        elif is_q_learner(model):
            # pass
            input[np] = input[np][:-1]
            output[np] = output[np][1:]
            yhat = model.model.forward(torch.Tensor(input[np]))
            for j in range(len(input[np])):
                batch_critic_loss[np] += sqr(output[np][j] - yhat[j])
            # model.optimizer.zero_grad()
            batch_count[np] += len(input[np])
            if i % 10 == 9:
                loss = batch_critic_loss[np] / batch_count[np]
                loss.backward()
                model.optimizer.step()
                model.optimizer.zero_grad()
                batch_critic_loss[np] = 0
                batch_count[np] = 0
                qlloss = loss
        else:
            print("incomplete model")
            exit(0)

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
        log_file.write(train_log + '\n')

        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([w0 / (w0 + w1 + 0.000000001), ]), win='p0 win percent',
        #          update='append' if not first else None, opts={'title': "p0 win percent"})
        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([total_score[0] / (total_round + 0.000000001), ]), win='scores/turns', name="p0",
        #          update='append' if not first else None, opts={'showlegend': True, 'title': "scores/turns"})
        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([total_score[1] / (total_round + 0.000000001), ]), win='scores/turns', name="p1",
        #          update='append' if not first else None)
        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([total_round / 10.0, ]), win='turns',
        #          update='append' if not first else None, opts={'title': "average end turn"})
        first = False
        total_score = [0, 0]
        total_round = 0
        w0 = 0
        w1 = 0

    if i % 100 == 0:
        for np in range(2):
            model = models[np]
            model.save('{}-{}p.pkl'.format(model.model_name, np + 1))
        with open('PPO-step.log', 'w+') as f:
            f.write(str(i))

    if i % 10000 == 0:
        for np in range(2):
            model = models[np]
            model.save('{}-{}p{}.pkl'.format(model.model_name, np + 1, i))

    # print("???", torch.sum(models[1].base_embedding))
    if ob['curr_turn'] < best_turn:
        best_turn = ob['curr_turn']
        json_replay = json.dumps(replay)
        with open('PPO_pro_play.json', 'w+') as f:
            f.write(json_replay)

    if ob['curr_turn'] == best_turn and (p0['score'] + p1['score']) / ob['curr_turn'] > best_avg_score:
        best_avg_score = (p0['score'] + p1['score']) / ob['curr_turn']
        json_replay = json.dumps(replay)
        with open('PPO_pro_play.json', 'w+') as f:
            f.write(json_replay)
