# Integrations: Telegram Bot Admin Panel

## 1. Обзор

Проект зависит от внешних и локальных сервисов:

- Telegram Bot API;
- LLM provider: OpenRouter или локальная Ollama;
- PostgreSQL;
- Railway для деплоя;
- optional: Hugging Face/OpenAI для voice/image расширений после MVP.

## 2. Integration Diagram

```mermaid
flowchart LR
    APP["Telegram Bot Admin Panel\nFastAPI + Bot Worker"]
    TG["Telegram Bot API"]
    OR["OpenRouter API"]
    OL["Ollama Local API"]
    PG[("PostgreSQL")]
    RW["Railway"]
    ENV["Environment Variables"]

    APP --> TG
    APP --> OR
    APP --> OL
    APP --> PG
    RW --> APP
    RW --> PG
    ENV --> APP
```

## 3. Telegram Bot API

| Параметр | Значение |
| --- | --- |
| Назначение | Получение сообщений пользователей и отправка ответов. |
| Auth | `TELEGRAM_BOT_TOKEN` в env. |
| MVP mode | Polling для локального запуска, webhook можно добавить для production. |
| Основные операции | `getUpdates`, `sendMessage`, `sendChatAction`, `getFile` для будущих voice/image. |

Риски:

- один token не может одновременно стабильно работать в нескольких polling-процессах;
- корпоративный SSL может ломать запросы;
- нельзя хранить token в Git.

Меры:

- документировать правило "один запущенный bot worker";
- хранить token только в `.env`/Railway variables;
- добавить `HTTP_SSL_VERIFY=false` только как локальный учебный обход, не как production default.

## 4. LLM Provider

### OpenRouter

| Параметр | Значение |
| --- | --- |
| Назначение | Облачная генерация ответов. |
| Auth | `OPENROUTER_API_KEY`. |
| Плюсы | Не требует локального железа, много моделей. |
| Минусы | Требует API key, зависит от сети и баланса. |

### Ollama

| Параметр | Значение |
| --- | --- |
| Назначение | Локальная генерация ответов. |
| Auth | Обычно не требуется локально. |
| URL | `OLLAMA_BASE_URL=http://localhost:11434`. |
| Пример модели | `llama3.2:3b`. |
| Плюсы | Бесплатно локально, хорошо для учебной практики. |
| Минусы | Railway не запускает локальную Ollama внутри MVP без отдельной настройки. |

Правило архитектуры:

- bot handler не вызывает OpenRouter/Ollama напрямую;
- все вызовы идут через `LLM Adapter`;
- активный provider/model читается из `bot_settings`.

## 5. PostgreSQL

| Параметр | Значение |
| --- | --- |
| Назначение | Основное хранилище. |
| Auth | `DATABASE_URL`. |
| Локально | Docker PostgreSQL или установленный PostgreSQL. |
| Production | Railway PostgreSQL. |

Храним:

- prompt versions;
- model settings;
- Telegram users;
- messages;
- errors;
- audit logs;
- admin sessions.

Риски:

- недоступность БД ломает bot worker;
- миграции могут не примениться на Railway;
- данные сообщений могут содержать персональную информацию.

Меры:

- health check;
- Alembic migrations;
- privacy note в README;
- не хранить секреты в таблицах.

## 6. Railway

| Параметр | Значение |
| --- | --- |
| Назначение | Облачный деплой приложения и PostgreSQL. |
| Secrets | Railway Variables. |
| Start command | `python -m app.main` или `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. |

Для MVP есть два варианта запуска:

1. Один процесс FastAPI + Bot Worker.
2. Два процесса: web и worker.

Для учебного MVP выбираем один процесс, если polling не конфликтует с deployment-платформой.

## 7. Optional Integrations After MVP

| Интеграция | Для чего | Когда добавлять |
| --- | --- | --- |
| faster-whisper | Локальная расшифровка voice | После текстового MVP. |
| OpenAI Whisper API | Облачная расшифровка voice | Если есть API key и нужен простой production path. |
| Vision model | Анализ изображений | После стабилизации text flow. |
| Sentry | Error monitoring | После базового error log. |
| Redis | Cache/settings/session | Если появится нагрузка или несколько процессов. |

## 8. Environment Variables

```env
APP_ENV=local
APP_SECRET_KEY=change-me
ADMIN_PASSWORD=change-me
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/bot_admin
TELEGRAM_BOT_TOKEN=change-me
LLM_PROVIDER=ollama
OPENROUTER_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b
HTTP_SSL_VERIFY=true
```

## 9. Integration Acceptance Criteria

- Telegram Bot API работает локально.
- LLM Adapter может ответить через выбранный provider.
- PostgreSQL доступен по `DATABASE_URL`.
- Railway variables покрывают все секреты.
- При ошибке интеграции запись появляется в `error_logs`.
- Секреты не отображаются в admin UI.
