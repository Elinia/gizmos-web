import copy
import json
from typing import TypedDict

from .types import Action, Observation
from .common import Stage
from .GizmosEnv import GizmosEnv


class ActionLog(TypedDict):
    name: str
    action: Action


Replay = list[Observation | ActionLog]


class GizmosEnvTraining(GizmosEnv):
    replay: Replay = []

    def __init__(self, model_name: str, player_num=2, max_gizmos_num=16, max_level3_gizmos_num=4, check=False, log=False):
        self.model_name = model_name
        super().__init__(player_num, max_gizmos_num, max_level3_gizmos_num, check, log)

    def reset(self):
        self.replay = []
        return super().reset()

    def get_reward(self, playerIndex: int):
        if self.state['curr_stage'] != Stage.GAME_OVER:
            return 0
        if self.truncated:
            return -999
        me = self.state['players'][playerIndex]

        rank: int = 1
        for player in self.state['players']:
            if player.index == me.index:
                continue
            if player.score > me.score or len(player.gizmos) > len(me.gizmos) or player.total_energy_num > me.total_energy_num:
                rank += 1

        # winner_reward = ((1 + self.player_num) * self.player_num) // 2
        # loser_reward = 1 - rank
        winner_reward = 1
        loser_reward = 0
        return winner_reward if rank == 1 else loser_reward

    def log_replay(self, observation: Observation | None = None, action: ActionLog | None = None):
        if observation == None:
            if action == None:
                return
            self.replay.append(copy.deepcopy(action))
        else:
            ob = copy.deepcopy(observation)
            del ob['gizmos']
            self.replay.append(ob)

    def step(self, playerIndex: int, action: Action):
        self.log_replay(
            action={'name': self.model_name + '_' + str(playerIndex) + 'p', 'action': action})
        return super().step(playerIndex, action)

    def observation(self, playerIndex: int | None = None) -> Observation:
        ob = super().observation(playerIndex)
        self.log_replay(observation=ob)
        return ob

    def save_replay(self, path='replay.json'):
        json_replay = json.dumps(self.replay)
        with open(path, 'w+') as f:
            f.write(json_replay)
