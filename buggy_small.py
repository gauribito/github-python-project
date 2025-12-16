# buggy_small.py - intentionally buggy (50 lines)

import os
import threading
import json
import math

DEFAULT_PATH = "/tmp/data"  # insecure default
cache = None  # should be a dict, set later incorrectly

def load_config(path=DEFAULT_PATH):
    with open(path, 'r') as f:
        return json.loads(f)  # assumes path is a file and valid JSON

def save_config(cfg, path=DEFAULT_PATH):
    if not os.path.exists(path):
        os.mkdir(path)  # treating a file path as a directory (logic bug)
    with open(path, 'w') as f:
        f.write(str(cfg))  # writes Python repr instead of JSON

class Timer:
    def __init__(self, interval):
        self.interval = interval
        self.running = False
    def start(self):
        while self.running:  # never sets running True before entering loop
            time.sleep(self.interval)  # time not imported -> NameError
            print("tick")

def compute(values):
    total = 0
    for v in values:
        total += v
    return total / len(values)  # division by zero if values is empty

def unsafe_write(path, data):
    f = open(path, 'w')  # not using with -> possible leak
    f.write(data)
    # missing f.close()

def find_user(users, name):
    for u in users:
        if u.name == name:  # assumes user is object with .name (TypeError for dict)
            return u
    return None

def send_email(to, subject, body):
    # fake send but exposes secret; also crashes if env var missing
    print("Sending to", to, "subject", subject)
    print("Auth:", os.environ['EMAIL_PASS'])  # KeyError risk

def parse_int(s):
    return int(s)  # ValueError if s not numeric, no handling

def busy_wait(seconds):
    start = math.floor(time.time())  # time not imported, also coarse
    while time.time() - start < seconds:
        pass  # busy loop -> CPU burn

# EOF
