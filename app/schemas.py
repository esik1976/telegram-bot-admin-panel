import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str


class ActiveBotSettingsResponse(BaseModel):
    system_prompt: str
    provider: str
    model: str
    temperature: float
    max_tokens: int


class PromptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content: str
    is_active: bool
    created_at: datetime
    created_by: str


class PromptCreate(BaseModel):
    content: str = Field(min_length=1)


class BotSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: str
    model: str
    temperature: float
    max_tokens: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BotSettingsUpdate(BaseModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    temperature: float = Field(ge=0, le=2)
    max_tokens: int = Field(ge=1, le=8000)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    first_seen_at: datetime
    last_seen_at: datetime
    message_count: int


class MessageRead(BaseModel):
    id: uuid.UUID
    telegram_user_id: uuid.UUID
    telegram_id: int
    username: str | None
    direction: str
    content_type: str
    content: str | None
    provider: str | None
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    created_at: datetime


class ErrorRead(BaseModel):
    id: uuid.UUID
    telegram_user_id: uuid.UUID | None
    telegram_id: int | None
    username: str | None
    source: str
    error_type: str
    message: str
    details: str | None
    created_at: datetime
    resolved: bool
    resolved_at: datetime | None


class TelegramUserEvent(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None


class MessageEvent(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    direction: str = Field(pattern="^(inbound|outbound)$")
    content_type: str = "text"
    content: str | None = None
    provider: str | None = None
    model: str | None = None


class ErrorEvent(BaseModel):
    telegram_id: int | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None
    source: str
    error_type: str
    message: str
    details: str | None = None


class CreatedResponse(BaseModel):
    id: uuid.UUID
    status: str = "created"
