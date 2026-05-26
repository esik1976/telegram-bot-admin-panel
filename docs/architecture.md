# Architecture: Telegram Bot Admin Panel

## 1. Архитектурный стиль

Для MVP используем модульный монолит:

- один Python-проект;
- один FastAPI backend;
- server-rendered admin UI;
- Telegram Bot Worker внутри того же приложения или отдельным процессом из того же кода;
- PostgreSQL как единое хранилище.

Такой подход проще для учебного проекта, но сохраняет нормальные границы между слоями: `web`, `api`, `services`, `bot_worker`, `db`.

## 2. Component Diagram

```mermaid
flowchart LR
    U["Telegram User"] --> TG["Telegram API"]
    TG --> BW["Bot Worker\npython-telegram-bot"]
    BW --> SVC["Service Layer"]
    BW --> LLM["LLM Adapter\nOpenRouter / Ollama"]
    LLM --> EXT["External or Local LLM"]

    A["Admin"] --> UI["Admin Web UI\nJinja2 Templates"]
    UI --> API["FastAPI Backend"]
    API --> SVC

    SVC --> DB[("PostgreSQL")]
    API --> AUTH["Auth / Session"]
    AUTH --> DB

    R["Railway"] -. deploy .-> API
    R -. managed db .-> DB
```

## 3. Layer Diagram

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer"]
        WEB["Admin pages\nlogin, dashboard, prompts, settings, users, messages, errors"]
        BOT["Telegram handlers\n/start, text, voice/image later"]
    end

    subgraph Application["Application Layer"]
        AUTH["Auth service"]
        SETTINGS["Settings service"]
        USERS["Users service"]
        MESSAGES["Messages service"]
        ERRORS["Errors service"]
        AUDIT["Audit service"]
    end

    subgraph Infrastructure["Infrastructure Layer"]
        DB["PostgreSQL / SQLAlchemy"]
        LLM["LLM providers"]
        TELEGRAM["Telegram API"]
    end

    WEB --> AUTH
    WEB --> SETTINGS
    WEB --> USERS
    WEB --> MESSAGES
    WEB --> ERRORS
    WEB --> AUDIT

    BOT --> SETTINGS
    BOT --> USERS
    BOT --> MESSAGES
    BOT --> ERRORS
    BOT --> LLM
    BOT --> TELEGRAM

    AUTH --> DB
    SETTINGS --> DB
    USERS --> DB
    MESSAGES --> DB
    ERRORS --> DB
    AUDIT --> DB
```

## 4. Request Flow: Telegram Message

```mermaid
sequenceDiagram
    participant User as Telegram User
    participant Telegram as Telegram API
    participant Bot as Bot Worker
    participant Settings as Settings Service
    participant LLM as LLM Adapter
    participant DB as PostgreSQL

    User->>Telegram: Sends message
    Telegram->>Bot: Update
    Bot->>DB: Upsert telegram_user
    Bot->>Settings: Get active prompt and model settings
    Settings->>DB: Read active settings
    DB-->>Settings: Settings
    Settings-->>Bot: Settings
    Bot->>LLM: Generate answer
    LLM-->>Bot: Answer
    Bot->>Telegram: Send answer
    Bot->>DB: Save inbound and outbound messages
```

## 5. Request Flow: Admin Changes Prompt

```mermaid
sequenceDiagram
    participant Admin
    participant Web as Admin Web UI
    participant Backend as FastAPI Backend
    participant Settings as Settings Service
    participant Audit as Audit Service
    participant DB as PostgreSQL

    Admin->>Web: Opens /prompts
    Web->>Backend: GET /prompts
    Backend->>DB: Check session
    DB-->>Backend: Session valid
    Backend-->>Web: Prompt form
    Admin->>Web: Saves new prompt
    Web->>Backend: POST /prompts
    Backend->>Settings: Save active prompt
    Settings->>DB: Insert prompt version and mark active
    Backend->>Audit: Write admin action
    Audit->>DB: Insert audit log
    Backend-->>Web: Redirect to /prompts
```

## 6. Deployment View

```mermaid
flowchart LR
    DEV["Local machine"] --> GIT["Git repository"]
    GIT --> RW["Railway service"]
    RW --> APP["Python app\nFastAPI + Bot Worker"]
    RW --> PG[("Railway PostgreSQL")]
    APP --> TG["Telegram API"]
    APP --> LLM["OpenRouter API or Ollama-compatible endpoint"]
    APP --> PG
```

## 7. Границы ответственности

| Зона | Что делает | Чего не делает |
| --- | --- | --- |
| `web` | HTML-страницы админки, формы, таблицы | Не содержит бизнес-логику хранения |
| `api` | JSON endpoints для health/internal operations | Не рендерит HTML |
| `services` | Бизнес-операции: settings, users, messages, errors, audit | Не зависит от Telegram UI |
| `bot_worker` | Telegram handlers, получение updates, отправка ответов | Не хранит SQL вручную, использует services |
| `llm` | Единый интерфейс к LLM provider | Не знает о web routes |
| `db/models` | Схема данных и подключение к БД | Не содержит сценарии пользователя |

## 8. Архитектурные решения

1. MVP строится как модульный монолит, потому что это быстрее для учебного запуска и проще деплоится.
2. Admin UI делается server-rendered, чтобы не добавлять frontend build pipeline.
3. Bot Worker и Web Backend используют общий service layer, чтобы не дублировать логику.
4. Секреты хранятся только в env/Railway variables.
5. Voice/image из урока 3 проектируются как расширение после базового текстового MVP.

## 9. Проверка архитектуры

- Можно локально запустить один Python-проект.
- Можно заменить LLM provider без переписывания Telegram handlers.
- Можно вынести Bot Worker в отдельный процесс позже, потому что он уже отделен от web routes.
- Можно добавить роли позже, потому что admin auth изолирован в отдельном модуле.
