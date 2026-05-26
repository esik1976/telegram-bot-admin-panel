import httpx
import re

from app.config import Settings
from app.models import BotSettings


class LLMError(RuntimeError):
    pass


async def generate_answer(
    *,
    user_message: str,
    system_prompt: str,
    bot_settings: BotSettings,
    app_settings: Settings,
) -> str:
    provider = bot_settings.provider.lower()
    if provider == "ollama":
        answer = await _generate_with_ollama(
            user_message=user_message,
            system_prompt=system_prompt,
            bot_settings=bot_settings,
            app_settings=app_settings,
        )
        return _apply_prompt_suffix_rule(answer, system_prompt)
    if provider == "openrouter":
        answer = await _generate_with_openrouter(
            user_message=user_message,
            system_prompt=system_prompt,
            bot_settings=bot_settings,
            app_settings=app_settings,
        )
        return _apply_prompt_suffix_rule(answer, system_prompt)
    raise LLMError(f"Unsupported LLM provider: {bot_settings.provider}")


def _apply_prompt_suffix_rule(answer: str, system_prompt: str) -> str:
    match = re.search(r'в конце добавляй:\s*[«"](.+?)[»"]', system_prompt, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return answer

    suffix = match.group(1).strip()
    if not suffix or suffix in answer:
        return answer
    return f"{answer.rstrip()}\n\n{suffix}"


async def _generate_with_ollama(
    *,
    user_message: str,
    system_prompt: str,
    bot_settings: BotSettings,
    app_settings: Settings,
) -> str:
    payload = {
        "model": bot_settings.model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "options": {
            "temperature": bot_settings.temperature,
            "num_predict": bot_settings.max_tokens,
        },
    }
    async with httpx.AsyncClient(verify=app_settings.http_ssl_verify, timeout=60) as client:
        response = await client.post(f"{app_settings.ollama_base_url}/api/chat", json=payload)
        response.raise_for_status()
    data = response.json()
    content = data.get("message", {}).get("content")
    if not content:
        raise LLMError("Ollama returned empty response")
    return str(content)


async def _generate_with_openrouter(
    *,
    user_message: str,
    system_prompt: str,
    bot_settings: BotSettings,
    app_settings: Settings,
) -> str:
    if not app_settings.openrouter_api_key:
        raise LLMError("OPENROUTER_API_KEY is not configured")

    payload = {
        "model": bot_settings.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": bot_settings.temperature,
        "max_tokens": bot_settings.max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {app_settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(verify=app_settings.http_ssl_verify, timeout=60) as client:
        response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        raise LLMError("OpenRouter returned empty response")
    return str(content)
