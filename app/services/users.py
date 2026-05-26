from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TelegramUser, utc_now


def upsert_telegram_user(
    db: Session,
    *,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
    language_code: str | None,
) -> TelegramUser:
    user = db.scalars(select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)).first()
    if user is None:
        user = TelegramUser(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            message_count=0,
        )
        db.add(user)
        db.flush()
    else:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.language_code = language_code
        user.last_seen_at = utc_now()

    user.message_count += 1
    return user
