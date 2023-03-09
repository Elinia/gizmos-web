import json
import os


class IDGen(object):
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

    def gen_unique_id(self, type: str, data: any = ''):
        meaning = '{}_{}'.format(type, data)
        if (meaning) not in self.d.keys():
            self.update_d(meaning)
        return self.d[meaning]
