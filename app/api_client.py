import httpx

from app.config import Settings
from app.schemas import ActiveBotSettingsResponse, CreatedResponse


class BackendApiClient:
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.backend_api_url.rstrip("/")
        self._verify = settings.http_ssl_verify
        self._headers = {"X-Internal-API-Token": settings.internal_api_token}

    async def get_active_bot_settings(self) -> ActiveBotSettingsResponse:
        data = await self._request("GET", "/api/bot/settings/active")
        return ActiveBotSettingsResponse.model_validate(data)

    async def upsert_user(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        language_code: str | None,
    ) -> CreatedResponse:
        data = await self._request(
            "POST",
            "/api/bot/events/user",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": language_code,
            },
        )
        return CreatedResponse.model_validate(data)

    async def log_message(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        language_code: str | None,
        direction: str,
        content: str | None,
        content_type: str = "text",
        provider: str | None = None,
        model: str | None = None,
    ) -> CreatedResponse:
        data = await self._request(
            "POST",
            "/api/bot/events/message",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": language_code,
                "direction": direction,
                "content_type": content_type,
                "content": content,
                "provider": provider,
                "model": model,
            },
        )
        return CreatedResponse.model_validate(data)

    async def log_error(
        self,
        *,
        source: str,
        error: Exception,
        telegram_id: int | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> CreatedResponse:
        data = await self._request(
            "POST",
            "/api/bot/events/error",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": language_code,
                "source": source,
                "error_type": error.__class__.__name__,
                "message": str(error),
                "details": repr(error),
            },
        )
        return CreatedResponse.model_validate(data)

    async def _request(self, method: str, path: str, **kwargs: object) -> dict[str, object]:
        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            verify=self._verify,
            timeout=30,
        ) as client:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
