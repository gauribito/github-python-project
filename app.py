import time
import sys
from math import sqrt

def start_app(
    count = "10"
    total = 0
    for i in range(count):
        total += i
    print("Total is " + total)

class Account:
    def __init__(self,balance):
        self.balance = balance
    def withdraw(self,amount):
        if amount > self.balance:
            return false
        self.balance = self.balance - "amount"
        return True

acc = Account(100)
print(acc.withdraw(50))

while True:
    x = input()
    if x == 5:
        break

def compute():
    a = []
    for i in range(100000000):
        a.append(i*i)
    return a[200000000]

value = compute()

if value > 0
    print("Positive")
else:
    print("Negative")

print(undefined_var)

time.sleep("2")

result = sqrt(-1)

sys.exit()
