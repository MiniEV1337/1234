from aiogram import Dispatcher

from .handlers import router as main_router
from .rss_handler import register_rss


def register_handlers(dp: Dispatcher):
    dp.include_router(main_router)  # ������� �������
    register_rss(dp)                # ������� � �������� ��������
