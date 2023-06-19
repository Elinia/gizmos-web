# import json
import torch
import copy
import random

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from ai_2p.utils import Replay, log_replay
    from ai_2p.IDGen import IDGen
    from ai_2p.TD3 import TD3, ReplayBuffer
    from env.types import ActionType
    from env.common import Stage
    from env.GizmosEnv import GizmosEnv

replay_buffer = ReplayBuffer()


def sqr(x):
    return x * x


env = GizmosEnv(player_num=2, log=False, check=False)

idg = IDGen(path='d.json')
models = [TD3(idg), TD3(idg)]
models[0].load("TD3-1p100.pkl")
models[1].load("TD3-2p100.pkl")
best_turn: int = 20
best_avg_score: float = 0.0

max_can_num = 0
ppo_actor_loss = 0
ppo_critic_loss = 0
batch_actor_loss = [0.0, 0.0]
batch_other_loss = [0.0, 0.0]
batch_critic_loss = [0.0, 0.0]
batch_count = [0.0, 0.0]


try:
    f = open('{}-step.log'.format("TD3"), 'r')
    start_step = int(f.read()) + 1
except FileNotFoundError:
    start_step = 0

for i in range(start_step, 10000000):
    env.reset()
    last_score = 0
    ret = 0
    input = [[], []]
    input_dense = [[], []]
    output = [[0, ], [0, ]]
    ppo_total_loss: list[list[torch.Tensor]] = [[], []]
    random_a = [[], []]
    action = [[], []]
    traj = []
    replay: Replay = []

    last_score = [0, 0]
    last_ball_num = [0, 0]
    while True:
        np = env.state['curr_player_index']
        model = models[np]
        ob = env.observation(np)
        log_replay(replay, observation=ob)
        action_space = ob['action_space']
        if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_turn'] > 25:
            break
        act = None
        ob_id, ob_dense = model.gen_ob_feature(ob)
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
            act_id, act_dense = model.gen_action_feature(action)
            ti_id.append(copy.copy(ob_id + act_id))
            ti_dense.append(copy.copy(ob_dense + act_dense))
            can_num += 1
        # print("all", can_num)
        max_can_num = max(max_can_num, can_num)

        yhat = model.forward(torch.Tensor(
            ti_id), torch.Tensor(ti_dense)).view(-1,)
        # def sample_gumbel(shape, eps=1e-20):
        #     U = torch.rand(shape)
        #     return -torch.log(-torch.log(U + eps) + eps)
        if random.random() < 0.001:
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

        traj.append(str(ob['curr_turn']) + ": " + str(act))
        act_id, act_dense = model.gen_action_feature(act)
        input[np].append(list(map(int, ob_id + act_id)))
        input_dense[np].append(list(map(float, ob_dense + act_dense)))

        # score_reward = (ob['players'][np]['score'] - last_score[np]) / 50.0
        # ball_reward = (ob['players'][np]['total_energy_num'] -
        #                last_ball_num[np]) / 100.0
        research_pay = 0
        if act['type'] == ActionType.PICK and ob['curr_stage'] == Stage.MAIN and ob['curr_turn'] > 10:
            research_pay -= 0.1
        if act['type'] == ActionType.RESEARCH:
            research_pay -= 0.1
        if act['type'] == ActionType.FILE:
            research_pay -= 0.1
        if act['type'] == ActionType.FILE_FROM_RESEARCH:
            research_pay -= 0.1
        if act['type'] == ActionType.GIVE_UP:
            research_pay -= 0.5
        if act['type'] == ActionType.BUILD:
            cost = act['cost_energy_num']['red'] + act['cost_energy_num']['black'] + act['cost_energy_num']['blue'] + act['cost_energy_num']['yellow']
            research_pay += 0.1 * cost
        if act['type'] == ActionType.BUILD_FROM_RESEARCH:
            cost = act['cost_energy_num']['red'] + act['cost_energy_num']['black'] + act['cost_energy_num']['blue'] + act['cost_energy_num']['yellow']
            research_pay += 0.1 * cost
        if act['type'] == ActionType.BUILD_FROM_FILED:
            cost = act['cost_energy_num']['red'] + act['cost_energy_num']['black'] + act['cost_energy_num']['blue'] + act['cost_energy_num']['yellow']
            research_pay += 0.1 * cost
        if act['type'] == ActionType.USE_GIZMO:
            research_pay += 0.1
        output[np].append(research_pay / 5)
        last_score[np] = ob['players'][np]['score']
        last_ball_num[np] = ob['players'][np]['total_energy_num']
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
        v = 0
        if np == winner:
            v += (27 - ob['curr_turn']) * (1 + ob['players'][np]
                                           ['score'] / 100.0 - ob['players'][1 - np]['score'] / 100.0)
        else:
            v -= 1.0

        output[np][-1] += v * 2
        # output[np].append(v)

    for np in range(2):
        model = models[np]

        for j in range(len(input[np])):
            if j == len(input[np]) - 1:
                replay_buffer.add(np, input[np][j], input_dense[np][j], input[np][j], input_dense[np][j],
                                  output[np][j + 1], 0)
            else:
                replay_buffer.add(np, input[np][j], input_dense[np][j], input[np]
                                  [j + 1], input_dense[np][j + 1], output[np][j + 1], 1)

        models[np].train(np, replay_buffer)

    if i == 0:
        continue
    if i % 100 == 0:
        print(traj)
        print("step", i)
    if i % 10 == 0:
        # raw_log = "Games played:", i, "; token seen:", idg.cnt, "; loss:", float(ppo_critic_loss), float(ppo_actor_loss), float(ppo_other_loss), "; end turn", ob[
        #     'curr_turn'], "; final score",  p0['score'],  p1['score'], '; maxcan:', max_can_num
        raw_log = "Games played:", i, "; token seen:", idg.cnt, "; end turn", ob[
            'curr_turn'], "; final score",  p0['score'],  p1['score'], '; maxcan:', max_can_num, "return: ", sum(output[0]), sum(output[1])
        # raw_log = "pass"
        train_log = ' '.join(map(lambda x: str(x), raw_log))
        print(train_log)
        with open('{}.log'.format("TD3"), 'a+') as log_file:
            log_file.write(train_log + '\n')

        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([w0 / (w0 + w1 + 0.000000001), ]), win='p0 win percent',
        #          update='append' if not first else None, opts={'title': "p0 win percent"})
        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([total_score[0] / (total_round + 0.000000001), ]), win='scores/turns', name="p0",
        #          update='append' if not first else None, opts={'showlegend': True, 'title': "scores/turns"})
        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([total_score[1] / (total_round + 0.000000001), ]), win='scores/turns', name="p1",
        #          update='append' if not first else None)
        # vis.line(X=torch.tensor([i, ]), Y=torch.tensor([total_round / 10.0, ]), win='turns',
        #          update='append' if not first else None, opts={'title': "average end turn"})
        # first = False
        # total_score = [0, 0]
        # total_round = 0
        # w0 = 0
        # w1 = 0
    #
    # if i % 100 == 0:
    #     for np in range(2):
    #         model = models[np]
    #         model.save('{}-{}p.pkl'.format(model_name, np + 1))
    #     with open('{}-step.log'.format(model_name), 'w+') as f:
    #         f.write(str(i))
    #
    if i % 100 == 0:
        for np in range(2):
            model = models[np]
            model.save('{}-{}p{}.pkl'.format("TD3", np + 1, i))
    #
    # if ob['curr_turn'] < best_turn:
    #     best_turn = ob['curr_turn']
    #     json_replay = json.dumps(replay)
    #     with open('{}_pro_play.json'.format(model_name), 'w+') as f:
    #         f.write(json_replay)
    #
    # if ob['curr_turn'] == best_turn and (p0['score'] + p1['score']) / ob['curr_turn'] > best_avg_score:
    #     best_avg_score = (p0['score'] + p1['score']) / ob['curr_turn']
    #     json_replay = json.dumps(replay)
    #     with open('{}_pro_play.json'.format(model_name), 'w+') as f:
    #         f.write(json_replay)
