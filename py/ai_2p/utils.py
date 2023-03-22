
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


def lget_attr(l: list, i: int, attr: str):
    x = lget(l, i)
    return x[attr] if x is not None else None


def lget_id(l: list, i: int):
    return lget_attr(l, i, 'id')


def lget_my_giz(l: list, i: int):
    return '{}_{}_{}'.format(lget_attr(l, i, 'id'), lget_attr(l, i, 'used'), lget_attr(l, i, 'active'))


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
