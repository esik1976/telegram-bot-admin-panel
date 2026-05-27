import traceback
import uuid

from sqlalchemy.orm import Session

from app.models import ErrorLog, TelegramUser, utc_now


def log_error(
    db: Session,
    *,
    source: str,
    error: Exception,
    telegram_user: TelegramUser | None = None,
) -> ErrorLog:
    entry = ErrorLog(
        telegram_user_id=telegram_user.id if telegram_user else None,
        source=source,
        error_type=error.__class__.__name__,
        message=str(error),
        details="".join(traceback.format_exception(error))[:4000],
    )
    db.add(entry)
    return entry


def resolve_error(db: Session, error_id: uuid.UUID) -> ErrorLog | None:
    entry = db.get(ErrorLog, error_id)
    if entry is None:
        return None
    entry.resolved = True
    entry.resolved_at = utc_now()
    return entry
