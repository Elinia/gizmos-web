from GizmosEnv import GizmosEnv
from common import Stage

env = GizmosEnv(player_num=1)

while env.state['curr_stage'] != Stage.GAME_OVER:
    # print(list(map(lambda g: g['id'], env.observation(0)['gizmos_board'][1])))
    env.step(0, env.sample())
    # print(len(env.observation(0)['action_space']))
