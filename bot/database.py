from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(Integer, primary_key=True)
    subscription_level = Column(Integer, default=0)
    night_news = Column(Boolean, default=False)
    favorite_categories = Column(String, default="[]")  # ������ ��� JSON-������

    def get_favorites(self):
        return json.loads(self.favorite_categories)

    def set_favorites(self, favs: list):
        self.favorite_categories = json.dumps(favs)


engine = create_engine("sqlite:///bot.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
