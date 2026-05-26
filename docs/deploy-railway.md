# Deploy To Railway

## 1. Подход

Для production лучше создать два Railway services из одного GitHub repository:

1. `bot-admin-web` - web-админка FastAPI.
2. `bot-admin-worker` - Telegram polling worker.

Оба сервиса используют одну PostgreSQL базу и одинаковые переменные окружения.

Railway позволяет задавать Start Command на уровне service. Это предпочтительнее, чем полагаться на `Procfile`.

## 2. Railway Services

### Service 1: Web

Start Command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Pre-deploy Command:

```bash
python -m alembic upgrade head
```

Healthcheck Path:

```text
/api/health
```

### Service 2: Worker

Start Command:

```bash
python -m app.bot_worker
```

Важно: worker service должен быть один. Если запустить два worker-а с одним `TELEGRAM_BOT_TOKEN`, Telegram вернет conflict по `getUpdates`.

## 3. Railway Variables

Обязательные:

```env
APP_ENV=production
APP_SECRET_KEY=replace-with-long-random-secret
ADMIN_PASSWORD=replace-with-strong-password
DATABASE_URL=${{Postgres.DATABASE_URL}}
TELEGRAM_BOT_TOKEN=replace-with-telegram-token
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=replace-with-openrouter-key
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen/qwen-2.5-7b-instruct
HTTP_SSL_VERIFY=true
```

Для локального Ollama на Railway `OLLAMA_BASE_URL=http://localhost:11434` не подойдет, если Ollama не развернута отдельным сервисом. Для облачного деплоя проще использовать OpenRouter.

## 4. Локальная Проверка Перед Деплоем

```powershell
C:\venvs\tg-admin-panel\Scripts\python.exe -m alembic upgrade head
C:\venvs\tg-admin-panel\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8015
```

Проверить:

```text
http://127.0.0.1:8015/api/health
```

Worker:

```powershell
C:\venvs\tg-admin-panel\Scripts\python.exe -m app.bot_worker
```

## 5. Smoke Test После Деплоя

1. Открыть Railway web URL.
2. Открыть `/api/health`.
3. Войти в `/login`.
4. Изменить prompt в `/prompts`.
5. Изменить модель в `/settings`.
6. Написать Telegram-боту.
7. Проверить `/users`, `/messages`, `/errors`.

## 6. Production Notes

- Не использовать `ADMIN_PASSWORD=change-me`.
- Не использовать `APP_SECRET_KEY=change-me`.
- Не коммитить `.env`.
- `HTTP_SSL_VERIFY=false` допустим только локально для корпоративной сети.
- Для Railway должен быть `HTTP_SSL_VERIFY=true`.
- Для стабильной работы polling должен быть запущен только один worker.
