from redis import Redis
from rq import Queue, Retry
from config import REDIS_URL

conn = Redis.from_url(REDIS_URL)
queues = {
    "premium": Queue("premium", connection=conn),
    "extended": Queue("extended", connection=conn),
    "basic": Queue("basic", connection=conn),
}

def send_news(user_id, text):
    print(f"📤 Отправка: {user_id} ← {text}")

def enqueue_news(user):
    q = queues.get(user.tariff, queues["basic"])
    q.enqueue(send_news, args=(user.id, "новость"), retry=Retry(max=3, interval=[30, 60]))
