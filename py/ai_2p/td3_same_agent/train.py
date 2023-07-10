import json

if True:
    import sys
    import os
    sys.path.append(os.path.realpath('../..'))
    from ai_2p.td3_same_agent.IDGen import IDGen
    from ai_2p.td3_same_agent.TD3 import TD3, ReplayBuffer
    from env.types import ActionType
    from env.common import Stage
    from env.GizmosEnvTraining import GizmosEnvTraining

replay_buffer = ReplayBuffer()


def sqr(x):
    return x * x


env = GizmosEnvTraining(player_num=2, model_name="TD3")

idg = IDGen(path='d.json')
model = TD3(idg, 'model/TD3.pkl')
best_turn: int = 20
best_avg_score: float = 0.0

ppo_actor_loss = 0
ppo_critic_loss = 0
batch_actor_loss = [0.0, 0.0]
batch_other_loss = [0.0, 0.0]
batch_critic_loss = [0.0, 0.0]
batch_count = [0.0, 0.0]

build_num = [0] * 112


try:
    f = open('log/{}-step.log'.format("TD3"), 'r')
    start_step = int(f.read()) + 1
except FileNotFoundError:
    start_step = 0

for i in range(start_step, 10000000):
    env.reset()
    input = [[], []]
    input_dense = [[], []]
    output = [[0, ], [0, ]]
    # traj = []

    last_score = [0, 0]
    last_ball_num = [0, 0]
    while True:
        np = env.state['curr_player_index']
        ob = env.observation(np)
        action_space = ob['action_space']
        if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_turn'] > 25:
            break

        act, id, dense = model.best_action(ob, eps=0.001)

        # traj.append(str(ob['curr_turn']) + ": " + str(act))
        input[np].append(id)
        input_dense[np].append(dense)

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
        if act['type'] == ActionType.BUILD_FOR_FREE:
            research_pay += 0.5
        if act['type'] in [ActionType.BUILD, ActionType.BUILD_FROM_FILED, ActionType.BUILD_FROM_RESEARCH]:
            cost = act['cost_energy_num']['red'] + act['cost_energy_num']['black'] + \
                act['cost_energy_num']['blue'] + \
                act['cost_energy_num']['yellow']
            research_pay += 0.1 * cost
        if act['type'] == ActionType.USE_GIZMO:
            research_pay += 0.1
        output[np].append(research_pay / 10)
        # output[np].append(0)
        last_score[np] = ob['players'][np]['score']
        last_ball_num[np] = ob['players'][np]['total_energy_num']
        env.step(np, act)
        if act['type'] in [ActionType.BUILD, ActionType.BUILD_FROM_FILED, ActionType.BUILD_FROM_RESEARCH, ActionType.BUILD_FOR_FREE]:
            build_num[act['id']] += 1

    ob = env.observation(0)
    p0 = ob['players'][0]
    p1 = ob['players'][1]
    for np in range(2):
        last = len(output[np]) - 1
        v = 0
        if ob['curr_stage'] != Stage.GAME_OVER or ob['truncated']:
            v -= 0.9
        elif np == ob['result'][0]:
            v += (26 - ob['curr_turn']) * (1 + ob['players'][np]
                                           ['score'] / 100.0 - ob['players'][1 - np]['score'] / 100.0)
            # v += 1.0
        else:
            v -= 1.0

        output[np][-1] += v * 2
        # output[np].append(v)

    for np in range(2):
        for j in range(len(input[np])):
            if j == len(input[np]) - 1:
                replay_buffer.add(np, input[np][j], input_dense[np][j], input[np][j], input_dense[np][j],
                                  output[np][j + 1], 0)
            else:
                replay_buffer.add(np, input[np][j], input_dense[np][j], input[np]
                                  [j + 1], input_dense[np][j + 1], output[np][j + 1], 1)

        model.train(np, replay_buffer)

    if i == 0:
        continue
    # if i % 100 == 0:
    #     print(traj)
    #     print("step", i)
    if i % 10 == 0:
        raw_log = "Games played:", i, "; token seen:", idg.cnt, "; end turn", ob[
            'curr_turn'], "; final score",  p0['score'],  p1['score'], "return: ", "{:.2f}".format(sum(output[0])), "{:.2f}".format(sum(output[1]))
        train_log = ' '.join(map(lambda x: str(x), raw_log))
        print(train_log)
        with open('log/TD3.log', 'a+') as log_file:
            log_file.write(train_log + '\n')

        _raw_log = i, ob['curr_turn'], p0['score'], p1['score']
        _train_log = ','.join([str(x) for x in _raw_log])
        with open('log/TD3.csv', 'a+') as log_file:
            log_file.write(_train_log + '\n')

    if i % 100 == 0:
        model.save('model/TD3.pkl')
        if i % 50000 == 0:
            model.save('model/TD3-{}.pkl'.format(i))
        with open('log/TD3-step.log', 'w+') as f:
            f.write(str(i))

    if i % 1000 == 0:
        res = {}
        for i, num in enumerate(build_num):
            res[str(i)] = num
        js = json.dumps(res)
        with open('r/TD3_build_num.json', 'w+') as f:
            f.write(js)

    turn = ob['curr_turn']
    s0 = p0['score']
    s1 = p1['score']
    if turn < best_turn:
        best_turn = turn
        env.save_replay('r/TD3_replay_{}_t{}_{}vs{}.json'.format(
            i, turn, s0, s1))

    if turn == best_turn and (s0 + s1) / turn > best_avg_score:
        best_avg_score = (s0 + s1) / turn
        env.save_replay('r/TD3_replay_{}_t{}_{}vs{}.json'.format(
            i, turn, s0, s1))
