# Telegram Bot Admin Panel

Учебный fullstack MVP: Telegram-бот + web-админка для управления prompt, model settings, пользователями, сообщениями и ошибками.

## Статус

Сейчас реализован первый foundation slice:

- FastAPI app;
- `/api/health`;
- admin login/logout;
- dashboard;
- страницы `/prompts` и `/settings`;
- страницы `/users`, `/messages`, `/errors`;
- API `/api/bot/settings/active`;
- Telegram Bot Worker command;
- logging users/messages/errors;
- конфигурация через `.env`;
- SQLAlchemy models;
- Alembic-заготовка.

## Локальный запуск

```powershell
cd "C:\Users\IStankevichus\OneDrive - ТОО Кар-тел\Рабочий стол\Курсы\Интенсив AI-кодинг ИИ-агентов\lessons\lesson-5-system-analysis-planning\practice\telegram-bot-admin-panel"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Если OneDrive или длинный путь ломают создание `.venv`, используй короткий путь:

```powershell
py -m venv C:\venvs\tg-admin-panel
C:\venvs\tg-admin-panel\Scripts\python.exe -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
Copy-Item .env.example .env
```

Отредактируй `.env`, особенно:

- `DATABASE_URL`
- `ADMIN_PASSWORD`
- `TELEGRAM_BOT_TOKEN`

Для локальной практики по умолчанию используется SQLite:

```env
DATABASE_URL=sqlite:///C:/Users/IStankevichus/AppData/Local/tg-admin-panel/bot_admin.db
```

Для Railway или PostgreSQL замени на:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/bot_admin
```

Railway PostgreSQL может отдавать `DATABASE_URL` в формате `postgresql://...`. Приложение автоматически преобразует его в `postgresql+psycopg://...`, чтобы использовать установленный драйвер `psycopg`.

Запуск web-приложения:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

или, если используешь короткий venv:

```powershell
C:\venvs\tg-admin-panel\Scripts\python.exe -m uvicorn app.main:app --reload
```

Проверка:

- Web: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/api/health`
- Login: `http://127.0.0.1:8000/login`
- Prompt: `http://127.0.0.1:8000/prompts`
- Settings: `http://127.0.0.1:8000/settings`
- Users: `http://127.0.0.1:8000/users`
- Messages: `http://127.0.0.1:8000/messages`
- Errors: `http://127.0.0.1:8000/errors`
- Active bot settings API: `http://127.0.0.1:8000/api/bot/settings/active`

## Telegram Bot Worker

Перед запуском укажи настоящий токен в `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:your-token
```

Если на корпоративной сети появляется `CERTIFICATE_VERIFY_FAILED`, для локальной учебной проверки поставь:

```env
HTTP_SSL_VERIFY=false
```

Запуск worker:

```powershell
C:\venvs\tg-admin-panel\Scripts\python.exe -m app.bot_worker
```

Важно: с одним Telegram token должен работать только один polling-процесс.

## Railway Deploy

Подробная инструкция: `docs/deploy-railway.md`.

Рекомендуемая схема:

- Railway service `bot-admin-web`;
- Railway service `bot-admin-worker`;
- Railway PostgreSQL;
- одинаковые variables у web и worker.

Start Command для web:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Start Command для worker:

```bash
python -m app.bot_worker
```

Pre-deploy Command для web:

```bash
python -m alembic upgrade head
```

## Database

Для `/api/health` нужна доступная база из `DATABASE_URL`. Локально можно использовать SQLite без установки PostgreSQL.

Применить миграции:

```powershell
C:\venvs\tg-admin-panel\Scripts\python.exe -m alembic upgrade head
```

Проверить импорт приложения:

```powershell
C:\venvs\tg-admin-panel\Scripts\python.exe -c "from app.main import app; print(app.title)"
```

## Документация

Проектная документация лежит в `docs/`:

- `product-brief.md`
- `requirements.md`
- `technical-spec.md`
- `architecture.md`
- `data-model.md`
- `integrations.md`
- `roadmap.md`
- `task-decomposition.md`
- `adr/ADR-001-modular-monolith.md`
