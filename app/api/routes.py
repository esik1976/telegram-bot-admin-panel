from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.services.settings import get_active_prompt, get_active_settings

router = APIRouter(prefix="/api")


@router.get("/health")
def health(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "environment": settings.app_env,
        "database": "ok",
    }


@router.get("/bot/settings/active")
def active_bot_settings(db: Session = Depends(get_db)) -> dict[str, str | float | int]:
    prompt = get_active_prompt(db)
    settings = get_active_settings(db)
    return {
        "system_prompt": prompt.content,
        "provider": settings.provider,
        "model": settings.model,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
    }
