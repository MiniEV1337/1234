from sqlalchemy import Column, String, Integer
from bot.db.base import Base

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(String, primary_key=True)
    subscription_level = Column(Integer, default=0)
    # ������ ��������� ����, ������� �����������
