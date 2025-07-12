import subprocess, time
from redis import Redis
from rq import Worker, Connection

conn = Redis.from_url("redis://redis:6379")
with Connection(conn):
    for w in Worker.all():
        idle = time.time() - w.last_heartbeat
        if idle > 600:
            subprocess.call(["supervisorctl", "restart", w.name.split(".")[0]])
