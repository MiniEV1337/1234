from aiogram import Bot
from config import TELEGRAM_TOKEN, ADMIN_IDS
import asyncio, logging
from redis import Redis
from rq import Worker, Connection

logging.basicConfig(filename="logs/crash.log", level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)

async def monitor():
    conn = Redis.from_url("redis://redis:6379")
    while True:
        with Connection(conn):
            for w in Worker.all():
                if w.get_current_job() and w.get_current_job().is_failed:
                    name = w.name.split(".")[0]
                    for admin in ADMIN_IDS:
                        await bot.send_message(admin, f"⚠️ Воркер {name} упал!")
        await asyncio.sleep(60)

asyncio.run(monitor())
