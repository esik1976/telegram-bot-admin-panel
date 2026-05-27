from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import ErrorLog, Message, TelegramUser
from app.repositories.users import TelegramUserRepository


def list_users(db: Session, limit: int = 100) -> list[TelegramUser]:
    return TelegramUserRepository(db).list_recent(limit=limit)


def list_messages(db: Session, limit: int = 100) -> list[Message]:
    return list(
        db.scalars(
            select(Message)
            .options(joinedload(Message.telegram_user))
            .order_by(Message.created_at.desc())
            .limit(limit)
        ).all()
    )


def list_errors(db: Session, limit: int = 100) -> list[ErrorLog]:
    return list(
        db.scalars(
            select(ErrorLog)
            .options(joinedload(ErrorLog.telegram_user))
            .order_by(ErrorLog.created_at.desc())
            .limit(limit)
        ).all()
    )
