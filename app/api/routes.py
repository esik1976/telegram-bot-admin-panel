import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.models import ErrorLog
from app.schemas import (
    ActiveBotSettingsResponse,
    BotSettingsRead,
    BotSettingsUpdate,
    CreatedResponse,
    ErrorEvent,
    ErrorRead,
    HealthResponse,
    MessageEvent,
    MessageRead,
    PromptCreate,
    PromptRead,
    TelegramUserEvent,
    UserRead,
)
from app.services.logs import list_errors, list_messages, list_users
from app.services.messages import log_message
from app.services.settings import create_prompt_version, get_active_prompt, get_active_settings, update_active_settings
from app.services.users import upsert_telegram_user

router = APIRouter(prefix="/api")


def require_internal_api_token(
    x_internal_api_token: Annotated[str | None, Header(alias="X-Internal-API-Token")] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    if x_internal_api_token and hmac.compare_digest(x_internal_api_token, settings.internal_api_token):
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid internal API token",
    )


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", environment=settings.app_env, database="ok")


@router.get("/bot/settings/active", response_model=ActiveBotSettingsResponse, summary="Active settings for bot worker")
def active_bot_settings(db: Session = Depends(get_db)) -> ActiveBotSettingsResponse:
    prompt = get_active_prompt(db)
    settings = get_active_settings(db)
    return ActiveBotSettingsResponse(
        system_prompt=prompt.content,
        provider=settings.provider,
        model=settings.model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )


@router.get("/users", response_model=list[UserRead], summary="List Telegram users")
def users(db: Session = Depends(get_db), limit: int = 100) -> list[UserRead]:
    return list_users(db, limit=limit)


@router.get("/messages", response_model=list[MessageRead], summary="List message log")
def messages(db: Session = Depends(get_db), limit: int = 100) -> list[MessageRead]:
    return [
        MessageRead(
            id=message.id,
            telegram_user_id=message.telegram_user_id,
            telegram_id=message.telegram_user.telegram_id,
            username=message.telegram_user.username,
            direction=message.direction,
            content_type=message.content_type,
            content=message.content,
            provider=message.provider,
            model=message.model,
            prompt_tokens=message.prompt_tokens,
            completion_tokens=message.completion_tokens,
            created_at=message.created_at,
        )
        for message in list_messages(db, limit=limit)
    ]


@router.get("/errors", response_model=list[ErrorRead], summary="List error log")
def errors(db: Session = Depends(get_db), limit: int = 100) -> list[ErrorRead]:
    return [
        ErrorRead(
            id=error.id,
            telegram_user_id=error.telegram_user_id,
            telegram_id=error.telegram_user.telegram_id if error.telegram_user else None,
            username=error.telegram_user.username if error.telegram_user else None,
            source=error.source,
            error_type=error.error_type,
            message=error.message,
            details=error.details,
            created_at=error.created_at,
            resolved=error.resolved,
        )
        for error in list_errors(db, limit=limit)
    ]


@router.get("/prompts/active", response_model=PromptRead, summary="Get active prompt")
def active_prompt(db: Session = Depends(get_db)) -> PromptRead:
    return get_active_prompt(db)


@router.post("/prompts", response_model=PromptRead, status_code=201, summary="Create prompt version")
def create_prompt(payload: PromptCreate, db: Session = Depends(get_db)) -> PromptRead:
    return create_prompt_version(db, payload.content)


@router.get("/settings/active", response_model=BotSettingsRead, summary="Get active model settings")
def active_settings(db: Session = Depends(get_db)) -> BotSettingsRead:
    return get_active_settings(db)


@router.put("/settings/active", response_model=BotSettingsRead, summary="Update active model settings")
def update_settings(payload: BotSettingsUpdate, db: Session = Depends(get_db)) -> BotSettingsRead:
    return update_active_settings(
        db,
        provider=payload.provider,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )


@router.post(
    "/bot/events/user",
    response_model=CreatedResponse,
    status_code=201,
    summary="Upsert Telegram user",
    dependencies=[Depends(require_internal_api_token)],
)
def bot_user_event(payload: TelegramUserEvent, db: Session = Depends(get_db)) -> CreatedResponse:
    user = upsert_telegram_user(
        db,
        telegram_id=payload.telegram_id,
        username=payload.username,
        first_name=payload.first_name,
        last_name=payload.last_name,
        language_code=payload.language_code,
    )
    db.commit()
    db.refresh(user)
    return CreatedResponse(id=user.id)


@router.post(
    "/bot/events/message",
    response_model=CreatedResponse,
    status_code=201,
    summary="Create bot message event",
    dependencies=[Depends(require_internal_api_token)],
)
def bot_message_event(payload: MessageEvent, db: Session = Depends(get_db)) -> CreatedResponse:
    user = upsert_telegram_user(
        db,
        telegram_id=payload.telegram_id,
        username=payload.username,
        first_name=payload.first_name,
        last_name=payload.last_name,
        language_code=payload.language_code,
    )
    message = log_message(
        db,
        telegram_user=user,
        direction=payload.direction,
        content=payload.content,
        content_type=payload.content_type,
        provider=payload.provider,
        model=payload.model,
    )
    db.commit()
    db.refresh(message)
    return CreatedResponse(id=message.id)


@router.post(
    "/bot/events/error",
    response_model=CreatedResponse,
    status_code=201,
    summary="Create bot error event",
    dependencies=[Depends(require_internal_api_token)],
)
def bot_error_event(payload: ErrorEvent, db: Session = Depends(get_db)) -> CreatedResponse:
    user = None
    if payload.telegram_id is not None:
        user = upsert_telegram_user(
            db,
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            language_code=payload.language_code,
        )
    error = ErrorLog(
        telegram_user_id=user.id if user else None,
        source=payload.source,
        error_type=payload.error_type,
        message=payload.message,
        details=payload.details,
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return CreatedResponse(id=error.id)
