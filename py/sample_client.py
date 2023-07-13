from typing import TypedDict
import socketio

from env.common import Stage
from env.types import Observation, Action, ActionType
# from ai_2p.td3.IDGen import IDGen
# from ai_2p.td3.TD3 import TD3
from ai_2p.td3_same_agent.IDGen import IDGen
from ai_2p.td3_same_agent.TD3 import TD3

# models = [
#     TD3(IDGen(path='ai_2p/td3/d.json'), path='ai_2p/td3/TD3-1p1687000.pkl'),
#     TD3(IDGen(path='ai_2p/td3/d.json'), path='ai_2p/td3/TD3-2p1687000.pkl')
# ]

model = TD3(IDGen(path='ai_2p/td3_same_agent/d.json'),
            path='ai_2p/td3_same_agent/TD3-1638200.pkl')


class Player(TypedDict):
    name: str
    index: int
    me: bool


sio = socketio.Client()

index: int | None = None
connected = False


def login(name: str):
    sio.emit('login', {'name': name}, namespace='/player')


def ready():
    sio.emit('ready', namespace='/player')


def step(action: Action):
    print('[step] {}'.format(action))
    sio.emit('action', action, namespace='/player')


@sio.event(namespace='/player')
def connect():
    print('[connect]')
    global connected
    connected = True


@sio.event(namespace='/player')
def connect_error(data):
    print('[connect_error]')


@sio.event(namespace='/player')
def disconnect():
    print('[disconnect]')
    global connected
    connected = False


@sio.event(namespace='/player')
def observation(ob: Observation):
    print('[observation] turn: {} stage: {} player index: {} score: {}'.format(
        ob['curr_turn'],
        ob['curr_stage'],
        ob['curr_player_index'],
        ob['players'][ob['curr_player_index']]['score']))
    global index
    if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_player_index'] != index:
        return
    ob['action_space'] = [action for action in ob['action_space']
                          if action['type'] != ActionType.END]
    # action, id, dense = models[index].best_action(ob)
    action, id, dense = model.best_action(ob)
    step(action)


@sio.event(namespace='/player')
def start(player_list: list[Player]):
    global index
    index = [player['index'] for player in player_list if player['me']][0]


@sio.event(namespace='/player')
def end():
    global index
    index = None


if __name__ == '__main__':
    sio.connect('http://localhost:9123')
    while True:
        cmd = input('> ')
        if cmd.startswith('login'):
            login(cmd.split(' ')[1] if len(cmd.split(' ')) > 1 else 'AI')
        elif cmd == 'ready':
            ready()
        elif cmd == 'exit':
            exit(0)
