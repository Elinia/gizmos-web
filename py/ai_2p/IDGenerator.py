import json
import os


class IDGenerator(object):
    def __init__(self, path='d.json'):
        self.d: dict[any, int] = {}
        self.cnt = 0
        self.path = path
        if os.path.isfile(path):
            with open(path, 'r') as f:
                self.d = json.loads(f.read())
                self.cnt = len(self.d)
        else:
            print('no saved d.json')

    def update_d(self, key):
        self.d[key] = self.cnt
        self.cnt += 1
        json_d = json.dumps(self.d)
        with open(self.path, 'w+') as f:
            f.write(json_d)

    def gen_unique_id(self, px, _data, i=-1, energy_flag=False):
        if i == -1:
            data = str(_data)
            if (px + data) not in self.d.keys():
                self.update_d((px + data))
            return self.d[(px + data)]
        else:
            data = _data
            name = px
            if len(data) <= i:
                name += "none"
            else:
                if energy_flag:
                    name += str(data[i])
                else:
                    name += str(data[i]['id']) + str(data[i]['used'])
            if (name) not in self.d.keys():
                self.update_d(name)
            return self.d[name]
