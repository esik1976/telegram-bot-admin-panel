from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import BotSettings, PromptVersion
from app.services.audit import write_audit_log

DEFAULT_PROMPT = "Ты полезный Telegram AI-ассистент. Отвечай кратко и понятно."
DEFAULT_PROVIDER = "ollama"
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 800


def get_active_prompt(db: Session) -> PromptVersion:
    prompt = db.scalars(
        select(PromptVersion)
        .where(PromptVersion.is_active.is_(True))
        .order_by(PromptVersion.created_at.desc())
    ).first()
    if prompt:
        return prompt

    prompt = PromptVersion(content=DEFAULT_PROMPT, is_active=True, created_by="system")
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def create_prompt_version(db: Session, content: str) -> PromptVersion:
    current_prompt = get_active_prompt(db)
    db.execute(update(PromptVersion).values(is_active=False))

    prompt = PromptVersion(content=content.strip(), is_active=True, created_by="admin")
    db.add(prompt)
    db.flush()

    write_audit_log(
        db,
        action="prompt.updated",
        entity_type="prompt_version",
        entity_id=prompt.id,
        before_value=current_prompt.content,
        after_value=prompt.content,
    )
    db.commit()
    db.refresh(prompt)
    return prompt


def get_active_settings(db: Session) -> BotSettings:
    settings = db.scalars(
        select(BotSettings)
        .where(BotSettings.is_active.is_(True))
        .order_by(BotSettings.updated_at.desc())
    ).first()
    if settings:
        return settings

    settings = BotSettings(
        provider=DEFAULT_PROVIDER,
        model=DEFAULT_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=DEFAULT_MAX_TOKENS,
        is_active=True,
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_active_settings(
    db: Session,
    *,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> BotSettings:
    current_settings = get_active_settings(db)
    before_value = (
        f"provider={current_settings.provider}; model={current_settings.model}; "
        f"temperature={current_settings.temperature}; max_tokens={current_settings.max_tokens}"
    )

    current_settings.provider = provider.strip()
    current_settings.model = model.strip()
    current_settings.temperature = temperature
    current_settings.max_tokens = max_tokens

    after_value = (
        f"provider={current_settings.provider}; model={current_settings.model}; "
        f"temperature={current_settings.temperature}; max_tokens={current_settings.max_tokens}"
    )

    write_audit_log(
        db,
        action="settings.updated",
        entity_type="bot_settings",
        entity_id=current_settings.id,
        before_value=before_value,
        after_value=after_value,
    )
    db.commit()
    db.refresh(current_settings)
    return current_settings
