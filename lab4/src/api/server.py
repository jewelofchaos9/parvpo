import redis
import os
import logging
from logfmt_logger import getLogger
import json
from flask import Flask, request
from rq import Queue
from rq.job import Job

conn = redis.Redis(
    host='redis',
    port=int(os.getenv('REDIS_PORT', '6379'))
)

"""
logging.basicConfig(level=logging.DEBUG, 
                    format=json.dumps({"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"})
)
"""

queue = Queue(connection=conn)
app = Flask(__name__)
logger = getLogger(__name__, logging.DEBUG)


def add_flag(flag: str, team_token: str):
    conn.set(flag, team_token)


def add_team(team_token: str):
    conn.set(team_token, int(os.getenv("DEFAULT_SCORE", 2500)))


@app.before_request
def log_request():
    app.logger.info('Request from %s to %s', request.remote_addr, request.path)


@app.route('/api/generate_error')
def error():
    app.logger.error('AAAAAAAAAAAA ERROR from %s to %s', request.remote_addr, request.path)
    1/0


@app.route('/api/submit_flag', methods=['POST'])
def submit_flag_endpoint():
    flag = request.form.get('flag', None)
    token = request.form.get('token', None)

    if flag is None or token is None:
        return {"error": "flag or token not setted"}

    job = queue.enqueue_call(
        "worker.submit_flag", args=(flag, token), result_ttl=5000
    )

    logger.info(f"Started job with id {job.get_id()}")

    return {"msg": "started submitting", "id": job.get_id()}


@app.route('/api/results/<job_id>', methods=['GET'])
def get_result(job_id):
    job = Job.fetch(job_id, connection=conn)

    if job.is_finished:
        return job.result

    return {"msg": "job not finished yet"}


""" 
Две нижележащие ручки дергает только админ автоматизированными средставми, поэтому все должно быть четко, можно поля не проверять
"""
@app.route('/api/add_team', methods=['POST'])
def add_team_endpoint():
    token = request.form.get('token')
    logger.info(f"adding team {token}")
    add_team(token)

    return {"msg": "success"}


@app.route('/api/add_flag', methods=['POST'])
def add_flag_endpoint():
    token = request.form.get('token')
    flag = request.form.get('flag')
    add_flag(flag, token)

    return {"msg": "success"}


if __name__ == "__main__":
    app.run('0.0.0.0', port=1337)
