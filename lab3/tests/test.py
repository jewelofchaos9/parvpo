import requests
import os
import time
from random import choices, choice
from concurrent.futures import ThreadPoolExecutor
from string import printable
from uuid import uuid4
from tqdm import tqdm

API_URL = os.getenv('API_URL', 'http://0.0.0.0:1337/api')
TEAMS = []
FLAGS = []
TASKS = []
TASKS_LENGTH = []
TRIES = 500
THREADS = 3


def random_string(length=15):
    return ''.join(choices(printable, k=length))


def add_team(team_token):
    return requests.post(
        f'{API_URL}/add_team', data={"token": team_token}
    )


def add_flag(team_token, flag):
    return requests.post(
        f'{API_URL}/add_flag', data={"token": team_token, "flag": flag}
    )


def submit_flag(team_token, flag):
    return requests.post(
        f'{API_URL}/submit_flag', data={"token": team_token, "flag": flag}
    )


def generate_info():
    for _ in range(100):
        team_token = str(uuid4())
        TEAMS.append(team_token)
        add_team(team_token)
    for _ in range(100):
        flag = random_string()
        team_token = choice(TEAMS)
        FLAGS.append(flag)
        add_flag(team_token, flag)


def random_submit():
    team = choice(TEAMS)
    flag = choice(FLAGS)
    task_id = submit_flag(team, flag).json()['id']
    TASKS.append(task_id)


def loader():
    for i in tqdm(range(TRIES)):
        random_submit()

def scrumber():
    for i in tqdm(range(TRIES)):
        random_submit()
        num_of_tasks = requests.get(f"{API_URL}/queue_length").json()['msg']
        TASKS_LENGTH.append([time.time(), num_of_tasks])


def kek():
    num_of_tasks = 1
    while num_of_tasks != 0:
        num_of_tasks = requests.get(f"{API_URL}/queue_length").json()['msg']
        TASKS_LENGTH.append([time.time(), num_of_tasks])
        print(TASKS_LENGTH)
        time.sleep(0.2)

def high_load():
    pool = ThreadPoolExecutor(max_workers=THREADS)
    for _ in range(THREADS - 1):
        pool.submit(loader)
    pool.submit(scrumber)
    pool.shutdown(wait=True)


def test():
    generate_info()
    high_load()
    task_id = TASKS[-1]
    time.sleep(3)
    requests.get(f"{API_URL}/results/{task_id}").text
    kek()
    print(TASKS_LENGTH)

if __name__ == "__main__":
    test()
