import copy
from typing import Literal, TypedDict
import socketio
from aiohttp import web

from env.types import Action, Observation
from env.common import Stage
from env.GizmosEnv import GizmosEnv

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)


class PlayerInfo(TypedDict):
    name: str
    ready: bool


class ActionLog(TypedDict):
    name: str
    action: Action


players_info: dict[str, PlayerInfo] = {}
players_sid: list[str] = []
global_env: GizmosEnv | None = None
replay: list[Observation | ActionLog] = []


def get_player_info(sid: str):
    info = players_info[sid]
    if not info:
        raise Exception('no player with socket id: {}'.format(sid))
    return info


def get_env():
    if not global_env:
        raise Exception('no env')
    return global_env


async def broadcast_action(sid: str, action: Action):
    info = get_player_info(sid)
    await sio.emit('action', {'name': info['name'],
                              'action': action}, namespace='/player')
    await sio.emit('action', {'name': info['name'],
                              'action': action}, namespace='/observer')
    replay.append({'name': info['name'], 'action': action})


async def broadcast_observation():
    env = get_env()
    for i, sid in enumerate(players_sid):
        observation = env.observation(i)
        await sio.emit('observation', observation, room=sid, namespace='/player')
        if i == observation['curr_player_index']:
            await sio.emit('observation', observation, namespace='/observer')
            clone = copy.deepcopy(observation)
            # clone.pop('gizmos')
            replay.append(clone)


async def broadcast_room():
    room_info = []
    for info in players_info.values():
        room_info.append({'name': info['name'], 'ready': info['ready']})
    await sio.emit('room', room_info, namespace='/player')
    await sio.emit('room', room_info, namespace='/observer')


async def start_game():
    print('[start_game]')
    global global_env, players_sid, replay
    replay = []
    global_env = GizmosEnv(player_num=len(players_info))
    players_sid = [sid for sid in players_info.keys()]
    for sid in players_info.keys():
        player_list = [{
            'name': get_player_info(_sid)['name'],
            'index': i,
            'me':_sid == sid
        } for i, _sid in enumerate(players_sid)]
        await sio.emit('start', player_list, room=sid, namespace='/player')

    player_list = [{
        'name': get_player_info(sid)['name'],
        'index': i,
    } for i, sid in enumerate(players_sid)]
    await sio.emit('start', player_list, namespace='/observer')

    await broadcast_observation()


async def end_game():
    global global_env, players_sid, replay
    global_env = None
    players_sid = []
    for info in players_info.values():
        info['ready'] = False
    await sio.emit('replay', replay, namespace='/player')
    await sio.emit('replay', replay, namespace='/observer')
    replay = []
    await sio.emit('end', namespace='/player')
    await sio.emit('end', namespace='/observer')
    await broadcast_room()


@sio.event(namespace='/player')
async def connect(sid: str, environ, auth):
    print('[connect] {}'.format(sid))
    await broadcast_room()


@sio.event(namespace='/player')
async def disconnect(sid: str):
    print('[disconnect] {}'.format(sid))
    if sid in players_info:
        players_info.pop(sid)
        await broadcast_room()
    # reconnect mechanism?
    if global_env is not None:
        await end_game()


@sio.event(namespace='/player')
async def login(sid: str, info: dict[Literal['name'], str]):
    name = info['name']
    print('[login] {} {}'.format(sid, name))
    if name in [_info['name'] for _info in players_info.values()]:
        await sio.emit('error', 'name exists', room=sid, namespace='/player')
        return
    players_info[sid] = {'name': name, 'ready': False}
    await broadcast_room()


@sio.event(namespace='/player')
async def ready(sid: str):
    print('[ready] {}'.format(sid))
    # game running
    if global_env is not None:
        return
    info = get_player_info(sid)
    info['ready'] = not info['ready']
    await broadcast_room()
    if len(players_info) >= 1 and all([info['ready'] for info in players_info.values()]):
        await start_game()


@sio.event(namespace='/player')
async def action(sid: str, action: Action):
    env = get_env()
    player_index = players_sid.index(sid)
    print('[action] {}, {}'.format(player_index, action))
    env.step(player_index, action)
    await broadcast_action(sid, action)
    await broadcast_observation()
    if env.state['curr_stage'] == Stage.GAME_OVER:
        await end_game()


@sio.event(namespace='/player')
async def observation(sid: str):
    env = get_env()
    player_index = players_sid.index(sid)
    await sio.emit('observation', env.observation(player_index), room=sid, namespace='/player')


@sio.event(namespace='/observer')
async def connect(sid: str, environ, auth):
    print('[connect] {}'.format(sid))
    await broadcast_room()
    if global_env is not None:
        player_list = [{
            'name': get_player_info(sid)['name'],
            'index': i,
        } for i, sid in enumerate(players_sid)]
        await sio.emit('start', player_list, namespace='/observer')


@sio.event(namespace='/observer')
async def disconnect(sid: str):
    print('[disconnect] {}'.format(sid))


@sio.event(namespace='/observer')
async def observation(sid: str):
    env = get_env()
    await sio.emit('observation', env.observation(env.state['curr_player_index']), room=sid, namespace='/observer')


if __name__ == '__main__':
    web.run_app(app=app, port=9123)
