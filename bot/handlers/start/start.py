from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я бот, который приносит тебе свежие новости 📬\n"
        "Напиши /help, чтобы узнать, на что я способен."
    )
