from sqlalchemy import Column, String, Text, DateTime
from bot.db.base import Base

class News(Base):
    __tablename__ = "news"

    uid = Column(String, primary_key=True)
    title = Column(Text)
    link = Column(String)
    category = Column(String)
    summary = Column(Text)
    published = Column(DateTime)
