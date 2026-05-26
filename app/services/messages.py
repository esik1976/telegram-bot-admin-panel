from sqlalchemy.orm import Session

from app.models import Message, TelegramUser


def log_message(
    db: Session,
    *,
    telegram_user: TelegramUser,
    direction: str,
    content: str | None,
    content_type: str = "text",
    provider: str | None = None,
    model: str | None = None,
) -> Message:
    message = Message(
        telegram_user_id=telegram_user.id,
        direction=direction,
        content_type=content_type,
        content=content,
        provider=provider,
        model=model,
    )
    db.add(message)
    return message
