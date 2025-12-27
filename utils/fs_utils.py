import os

def ensure(path):
    os.makedirs(path, exist_ok=True)
