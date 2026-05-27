from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TelegramUser


class TelegramUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_telegram_id(self, telegram_id: int) -> TelegramUser | None:
        return self._db.scalars(
            select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
        ).first()

    def add(self, user: TelegramUser) -> TelegramUser:
        self._db.add(user)
        self._db.flush()
        return user

    def list_recent(self, limit: int = 100) -> list[TelegramUser]:
        return list(
            self._db.scalars(
                select(TelegramUser)
                .order_by(TelegramUser.last_seen_at.desc())
                .limit(limit)
            ).all()
        )
