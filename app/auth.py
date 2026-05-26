import hmac
import time
from hashlib import sha256
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status

from app.config import Settings, get_settings

SESSION_COOKIE_NAME = "admin_session"
SESSION_TTL_SECONDS = 60 * 60 * 8


def _sign(value: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), value.encode("utf-8"), sha256).hexdigest()


def create_session_token(settings: Settings) -> str:
    issued_at = str(int(time.time()))
    signature = _sign(issued_at, settings.app_secret_key)
    return f"{issued_at}.{signature}"


def verify_session_token(token: str | None, settings: Settings) -> bool:
    if not token or "." not in token:
        return False

    issued_at, signature = token.split(".", 1)
    expected_signature = _sign(issued_at, settings.app_secret_key)
    if not hmac.compare_digest(signature, expected_signature):
        return False

    try:
        issued_at_value = int(issued_at)
    except ValueError:
        return False

    return time.time() - issued_at_value <= SESSION_TTL_SECONDS


def verify_admin_password(password: str, settings: Settings) -> bool:
    return hmac.compare_digest(password, settings.admin_password)


def require_admin(
    admin_session: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    if verify_session_token(admin_session, settings):
        return
    raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
