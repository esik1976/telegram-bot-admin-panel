import traceback

from sqlalchemy.orm import Session

from app.models import ErrorLog, TelegramUser


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
