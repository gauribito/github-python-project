# broken_app.py

import math
import time
import os

def main():
    print("Starting Broken Python App...")

    # --- Syntax error: missing parenthesis ---
    if True:
        print("This won't compile"  

    # --- Logical error: division by zero ---
    x = 10
    y = 0
    print("Division:", x / y)

    # --- Runtime error: index out of bounds ---
    arr = [1, 2, 3]
    print("4th element:", arr[3])

    # --- Accessibility issue: hardcoded credentials ---
    username = "admin"
    password = "12345"
    print("Logging in with", username, password)

    # --- Resource leak: file opened but never closed ---
    f = open("nonexistent.txt", "r")
    print(f.read())

    # --- Wrong type conversion ---
    s = "hello"
    n = int(s)   # ValueError at runtime

    # --- Performance issue: infinite loop ---
    while True:
        print("Looping forever...")

    # --- Unreachable code below because of infinite loop ---

    # --- Goroutine-like leak using threads ---
    import threading
    t = threading.Thread(target=spam_forever)
    t.start()

    # --- Logical error: factorial of negative number ---
    print("Factorial(-5):", factorial(-5))

    # --- Math domain error ---
    print("Sqrt(-9):", math.sqrt(-9))

    # --- Inefficient sleep ---
    time.sleep(999999999999)

def spam_forever():
    while True:
        print("Spamming thread... no exit")
        time.sleep(1)

def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)  # infinite recursion if n < 0

main()
