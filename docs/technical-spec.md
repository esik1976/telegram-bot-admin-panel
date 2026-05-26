# Technical Spec: Telegram Bot Admin Panel

## 1. Цель

Создать учебный fullstack-проект: Telegram-бот с web-админкой, где администратор управляет поведением бота без изменения кода.

MVP должен показать полный цикл:

- Telegram Bot принимает сообщения пользователей.
- Backend хранит настройки, пользователей, сообщения, ошибки и audit log.
- Web Admin Panel позволяет администратору смотреть состояние системы и менять настройки.
- PostgreSQL используется как основное хранилище.
- Проект можно запустить локально и развернуть в Railway.

## 2. Scope MVP

### Входит

- Telegram bot polling или webhook mode.
- Web admin panel с авторизацией администратора.
- Dashboard со статусом и счетчиками.
- CRUD для активного system prompt.
- CRUD для LLM settings.
- Просмотр пользователей Telegram.
- Просмотр сообщений.
- Просмотр ошибок.
- Audit log для изменений настроек.
- PostgreSQL schema.
- README и документация запуска.

### Не входит

- Мультиорганизации.
- Сложная RBAC-модель.
- Биллинг.
- Рассылки.
- Ручной ответ оператора из админки.
- Отдельный frontend SPA, если достаточно server-rendered UI.
- Kubernetes и сложная инфраструктура.

## 3. Предлагаемый стек

| Слой | Технология | Обоснование |
| --- | --- | --- |
| Language | Python 3.11+ | Уже используется в предыдущих уроках для Telegram-ботов. |
| Bot | python-telegram-bot | Знакомая библиотека из уроков 2-3. |
| Backend | FastAPI | Простая API-разработка, OpenAPI из коробки, удобно для учебного проекта. |
| UI | Jinja2 templates + HTML/CSS | Минимум сборки и зависимостей, легко деплоить на Railway. |
| DB | PostgreSQL | Подходит для Railway и реального backend-проекта. |
| ORM | SQLAlchemy | Стандартный Python-подход к моделям и миграциям. |
| Migrations | Alembic | Контролируемые изменения схемы БД. |
| Auth | Cookie session + admin password from env | Достаточно для MVP с одним админом. |
| LLM Provider | OpenRouter или Ollama adapter | Можно поддержать облачную и локальную модель через общий интерфейс. |
| Deploy | Railway | Продолжает практику урока 2. |

## 4. Основные модули

```text
telegram-bot-admin-panel/
  app/
    main.py              # FastAPI app
    config.py            # env settings
    db.py                # database engine/session
    models.py            # SQLAlchemy models
    schemas.py           # Pydantic schemas
    auth.py              # admin auth/session helpers
    llm.py               # LLM provider interface
    bot_worker.py        # Telegram bot startup and handlers
    services/
      settings.py        # prompt/model settings logic
      messages.py        # message logging
      users.py           # Telegram user tracking
      errors.py          # error logging
      audit.py           # admin action logging
    web/
      routes.py          # admin pages
    api/
      routes.py          # JSON API endpoints
  templates/
    login.html
    dashboard.html
    settings.html
    prompts.html
    users.html
    messages.html
    errors.html
  static/
    styles.css
  migrations/
  tests/
  README.md
  requirements.txt
  .env.example
```

## 5. Runtime Components

| Компонент | Ответственность |
| --- | --- |
| Admin Web UI | Страницы для входа, dashboard, prompt/model settings, users, messages, errors. |
| FastAPI Backend | Авторизация, HTML routes, JSON API, бизнес-логика, доступ к БД. |
| Bot Worker | Получает Telegram updates, вызывает LLM, сохраняет пользователей/сообщения/ошибки. |
| LLM Adapter | Единый интерфейс для OpenRouter/Ollama или другого провайдера. |
| PostgreSQL | Хранит настройки, пользователей, сообщения, ошибки, audit log. |
| Railway | Запускает приложение и PostgreSQL в облаке. |

## 6. API Endpoints

### Web Pages

| Method | Path | Назначение |
| --- | --- | --- |
| GET | `/login` | Страница входа. |
| POST | `/login` | Проверка пароля администратора. |
| POST | `/logout` | Завершение сессии. |
| GET | `/` | Dashboard. |
| GET | `/prompts` | Просмотр и редактирование active prompt. |
| POST | `/prompts` | Сохранение active prompt. |
| GET | `/settings` | Просмотр и редактирование LLM settings. |
| POST | `/settings` | Сохранение LLM settings. |
| GET | `/users` | Список Telegram-пользователей. |
| GET | `/messages` | История сообщений. |
| GET | `/errors` | Журнал ошибок. |

### Internal API

| Method | Path | Назначение |
| --- | --- | --- |
| GET | `/api/health` | Проверка состояния приложения. |
| GET | `/api/bot/settings/active` | Активный prompt и LLM settings для Bot Worker. |
| POST | `/api/events/message` | Запись события сообщения, если Bot Worker вынесен отдельно. |
| POST | `/api/events/error` | Запись ошибки, если Bot Worker вынесен отдельно. |

В MVP Bot Worker может жить в одном процессе с FastAPI и вызывать service layer напрямую без HTTP.

## 7. Данные

Основные сущности:

- `admin_sessions`
- `bot_settings`
- `prompt_versions`
- `telegram_users`
- `messages`
- `error_logs`
- `audit_logs`

Детальная модель данных будет описана в `data-model.md`.

## 8. Потоки

### Сообщение пользователя

1. Пользователь пишет в Telegram.
2. Bot Worker получает update.
3. Bot Worker создает или обновляет `telegram_user`.
4. Bot Worker читает active prompt и LLM settings.
5. Bot Worker вызывает LLM Adapter.
6. Bot Worker отправляет ответ в Telegram.
7. Bot Worker сохраняет входящее и исходящее сообщение.
8. При ошибке Bot Worker сохраняет запись в `error_logs`.

### Изменение prompt

1. Admin открывает `/prompts`.
2. Backend проверяет сессию.
3. Admin сохраняет новый prompt.
4. Backend создает новую `prompt_version`.
5. Backend помечает новую версию активной.
6. Backend пишет событие в `audit_logs`.
7. Новые сообщения бота используют новый prompt.

## 9. Конфигурация

`.env`:

```env
APP_ENV=local
APP_SECRET_KEY=change-me
ADMIN_PASSWORD=change-me
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/bot_admin
TELEGRAM_BOT_TOKEN=change-me
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b
```

Правило: секреты не коммитятся, в репозитории хранится только `.env.example`.

## 10. Проверка MVP

Минимальный чек:

1. Запустить PostgreSQL.
2. Применить миграции.
3. Запустить приложение.
4. Войти в admin panel.
5. Изменить system prompt.
6. Написать Telegram-боту.
7. Проверить, что ответ использует новый prompt.
8. Проверить, что user/message/error/audit записи видны в панели.

## 11. Риски

| Риск | Как снизить |
| --- | --- |
| Telegram polling конфликтует с другим запущенным ботом | Документировать правило: одновременно работает только один процесс с этим token. |
| Секреты попадают в Git | `.gitignore`, `.env.example`, проверка перед commit. |
| БД недоступна | Понятное логирование ошибки, health endpoint, fallback message пользователю. |
| UI разрастается | Для MVP использовать server-rendered pages и простые таблицы. |
| Слишком много функций из урока 3 | Вынести voice/image в optional extension после базового MVP. |

## 12. Definition Of Done

- Есть работающий локальный запуск.
- Есть README с командами.
- Есть PostgreSQL schema и миграции.
- Admin может управлять prompt/model settings.
- Bot использует настройки из БД.
- История пользователей, сообщений и ошибок видна в web-панели.
- Есть architecture, data model, roadmap, task decomposition и минимум один ADR.
