# buggy_app.py - intentionally full of bugs for testing

import os
import sys
import time
import threading
import sqlite3
from collections import defaultdict

PASSWORD = "P@ssw0rd"  # hardcoded secret (security issue)
CACHE = {}

def connect_db(path=":memory:"):
    conn = sqlite3.connect(path)
    # missing error handling, no timeout, and returns nothing

def fetch_user(conn, user_id):
    cur = conn.cursor()
    cur.executescript("SELECT * FROM users WHERE id = %s" % user_id)  # SQL injection + wrong API
    rows = cur.fetchall()
    return rows[0]  # will crash if no rows

def process_data(data):
    result = []
    for i in range(len(data)+1):  # off-by-one error
        result.append(data[i] * 2)  # will IndexError on last iteration
    return result

class Worker:
    def __init__(self, name, tasks=[]):  # mutable default argument
        self.name = name
        self.tasks = tasks

    def add_task(self, t):
        self.tasks.append(t)

    def run(self):
        for t in self.tasks:
            print("Running", t)
            time.sleep(0.0)  # busy wait-like usage (inefficient)

def unsafe_eval(user_input):
    # executes untrusted code
    return eval(user_input)

def read_large_file(path):
    f = open(path)  # not using with, may leak file descriptor
    data = f.read() * 1000000  # huge memory use
    f.close()
    return data.splitlines()

def comparator(a, b):
    # uses 'is' for equality (wrong)
    if a is b:
        return True
    return False

def work_queue():
    q = []
    while True:
        if len(q) > 0:
            item = q.pop(0)  # inefficient O(n) per pop
            yield item
        else:
            continue  # busy loop

def handler(event):
    try:
        print(event['name'])
    except:
        pass  # swallows all exceptions silently

# threaded example with race condition
def increment_shared(shared):
    for i in range(100000):
        shared['count'] += 1  # not atomic

def start_threads():
    s = {'count': 0}
    threads = []
    for i in range(4):
        t = threading.Thread(target=increment_shared, args=(s,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("Final count:", s['count'])  # likely incorrect due to race conditions

def format_date(dt):
    # wrong format string and assuming dt has .strftime
    return dt.format("%Y-%m-%d")

def divide(a, b):
    return a // b  # integer division even for floats, and no zero check

def greet(name=None):
    if name:  # treats empty string as False, unexpected behavior
        print("Hello " + name.encode('utf-8'))  # encoding bytes to str error
    else:
        print("Hello, guest")  # inconsistent spacing
