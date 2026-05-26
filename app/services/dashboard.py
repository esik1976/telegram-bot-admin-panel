from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ErrorLog, Message, TelegramUser


def get_dashboard_stats(db: Session) -> dict[str, int]:
    return {
        "users_count": db.scalar(select(func.count(TelegramUser.id))) or 0,
        "messages_count": db.scalar(select(func.count(Message.id))) or 0,
        "errors_count": db.scalar(select(func.count(ErrorLog.id))) or 0,
    }
