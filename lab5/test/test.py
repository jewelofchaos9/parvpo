import requests
import os
import time
from random import choices, choice
from concurrent.futures import ThreadPoolExecutor
from string import printable
from uuid import uuid4
from tqdm import tqdm

API_URL = os.getenv('API_URL', 'http://0.0.0.0:3232/api')
THREADS = 1
TRIES = 100
IPS = []
with open('./ips.txt', 'r') as f:
    for line in f.readlines():
        IPS.append(line.strip())

def loader():
    for i in tqdm(range(TRIES)):
        try:
            requests.get(f"{API_URL}/get_bar?ip={choice(IPS)}").json()
        except:
            continue

def high_load():
    pool = ThreadPoolExecutor(max_workers=THREADS)
    for _ in range(THREADS):
        pool.submit(loader)
    pool.shutdown(wait=True)


def test():
    start = time.time()
    high_load()
    print(time.time() - start)

if __name__ == "__main__":
    test()
