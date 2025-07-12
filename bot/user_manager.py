from database import Session, User
import json

def get_or_create_user(telegram_id: int) -> User:
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    session.close()
    return user

def set_subscription(telegram_id: int, level: int):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.subscription_level = level
        session.commit()
    session.close()

def get_subscription(telegram_id: int) -> int:
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    level = user.subscription_level if user else 0
    session.close()
    return level

def toggle_night_news(telegram_id: int) -> bool:
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, night_news=True)
        session.add(user)
        session.commit()
        session.close()
        return True
    user.night_news = not user.night_news
    session.commit()
    new_state = user.night_news
    session.close()
    return new_state

def is_night_enabled(telegram_id: int) -> bool:
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    night = user.night_news if user else False
    session.close()
    return night

def save_favorites(telegram_id: int, categories: list[str]):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.favorite_categories = json.dumps(categories)
        session.commit()
    session.close()

def get_favorites(telegram_id: int) -> list[str]:
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user and user.favorite_categories:
        try:
            return json.loads(user.favorite_categories)
        except Exception:
            return []
    session.close()
    return []
