from typing import TypedDict
import socketio

from env.common import Stage
from env.types import Observation, Action
from ai_2p.Critic import Critic
from ai_2p.IDGenerator import IDGenerator

idg = IDGenerator(path='ai_2p/d.json')
critics = [Critic(64 + 4, idg=idg, path='ai_2p/cri-1p.pkl'),
           Critic(64 + 4, idg=idg, path='ai_2p/cri-2p.pkl')]


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
    global index
    if ob['curr_stage'] == Stage.GAME_OVER or ob['curr_player_index'] != index:
        return
    action = critics[index].best_action(ob)
    step(action)


@sio.event(namespace='/player')
def start(player_list: list[Player]):
    global index
    index = [player['index'] for player in player_list if player['me']][0]
    sio.emit('observation', namespace='/player')


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
