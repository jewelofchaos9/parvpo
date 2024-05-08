import redis
import os
import logging
from rq import Worker, Queue, Connection


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
conn = redis.Redis(
    host='redis',
    port=int(os.getenv('REDIS_PORT', '6379'))
)


def submit_flag(flag: str, team_token: str):
    flag_team_token = conn.get(flag)

    if flag_team_token is None:
        logger.info(f"team {team_token} submitted non-existing flag {flag}")
        return {"error": "flag doesnt exist"}

    if flag_team_token == team_token:
        logger.info(f"team {team_token} submitted their flag {flag}")
        return {"error": "you cannot submit your own flags"}

    """other team loses 1 point
    and submitter receives 1 point
    """
    other_team_score = int(conn.get(flag_team_token))
    conn.set(flag_team_token, other_team_score - 1)

    team_score = int(conn.get(team_token))
    conn.set(team_token, team_score + 1)

    return {"msg": "success"}


if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(list(map(Queue, ['default'])))
        worker.work()
