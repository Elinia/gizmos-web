
import copy
from typing import TypedDict


if True:
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    from env.types import Observation, Action


class ActionLog(TypedDict):
    name: str
    action: Action


Replay = list[Observation | ActionLog]


def lget(l: list, i: int):
    return l[i] if i < len(l) else None


def lget_id(l: list, i: int):
    x = lget(l, i)
    return x['id'] if x is not None else None


def log_replay(replay: list[Observation | ActionLog],
               observation: Observation | None = None,
               action: ActionLog | None = None):
    if observation == None:
        if action == None:
            return
        replay.append(copy.deepcopy(action))
    else:
        ob = copy.deepcopy(observation)
        del ob['gizmos']
        replay.append(ob)
