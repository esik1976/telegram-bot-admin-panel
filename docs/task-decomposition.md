# Task Decomposition: Telegram Bot Admin Panel

## Iteration 0: Project Foundation

- [x] Создать папку проекта.
- [x] Создать Python virtual environment.
- [x] Добавить `requirements.txt`.
- [x] Создать структуру `app/`, `templates/`, `static/`, `tests/`, `migrations/`.
- [x] Добавить `app/config.py`.
- [x] Добавить `.env.example`.
- [x] Добавить FastAPI app в `app/main.py`.
- [x] Добавить `/api/health`.
- [x] Подключить PostgreSQL через SQLAlchemy.
- [x] Настроить Alembic.
- [x] Создать первые миграции.
- [x] Обновить README командами локального запуска.

## Iteration 1: Admin Auth And Dashboard

- [x] Создать `app/auth.py`.
- [x] Реализовать проверку `ADMIN_PASSWORD`.
- [x] Реализовать cookie session.
- [x] Создать `templates/login.html`.
- [x] Создать layout для admin pages.
- [x] Создать dashboard route.
- [x] Создать dashboard template.
- [x] Добавить счетчики users/messages/errors.
- [x] Добавить базовые стили.
- [x] Проверить закрытие страниц без авторизации.

## Iteration 2: Prompt And Model Settings

- [x] Создать модели `PromptVersion` и `BotSettings`.
- [x] Создать services для prompt/settings.
- [x] Создать страницу `/prompts`.
- [x] Реализовать сохранение новой версии prompt.
- [x] Создать страницу `/settings`.
- [x] Реализовать сохранение provider/model/temperature/max_tokens.
- [x] Создать audit log model.
- [x] Логировать изменения prompt/settings.
- [x] Добавить seed initial prompt/settings.

## Iteration 3: Telegram Bot Integration

- [x] Создать `app/bot_worker.py`.
- [x] Подключить `python-telegram-bot`.
- [x] Реализовать `/start`.
- [x] Реализовать text message handler.
- [x] Создать `telegram_users` model/service.
- [x] Создать `messages` model/service.
- [x] Создать `app/llm.py`.
- [x] Реализовать Ollama provider.
- [x] Реализовать OpenRouter provider как optional.
- [x] Подставлять active prompt/settings в LLM request.
- [x] Сохранять inbound/outbound messages.
- [ ] Проверить, что изменение prompt влияет на новые ответы.

## Iteration 4: Logs And Observability

- [x] Создать `error_logs` model/service.
- [x] Логировать ошибки Telegram/LLM/DB.
- [x] Создать страницу `/users`.
- [x] Создать страницу `/messages`.
- [x] Создать страницу `/errors`.
- [x] Добавить фильтр последних N записей.
- [ ] Добавить resolved flag для ошибок.
- [x] Проверить отображение ошибок в UI.

## Iteration 5: Deploy

- [x] Подготовить Railway project.
- [ ] Добавить PostgreSQL plugin/service.
- [x] Задать `DATABASE_URL`.
- [x] Задать `TELEGRAM_BOT_TOKEN`.
- [x] Задать `ADMIN_PASSWORD`.
- [x] Задать LLM provider variables.
- [x] Настроить start command.
- [x] Применить миграции.
- [x] Проверить web health endpoint.
- [ ] Проверить ответ Telegram-бота.
- [x] Обновить README с production notes.

## Iteration 6: Optional Multimodal Extension

- [ ] Добавить флаги `voice_enabled` и `image_enabled`.
- [ ] Добавить обработку voice messages.
- [ ] Подключить local ASR или Whisper API.
- [ ] Добавить обработку image messages.
- [ ] Подключить vision provider.
- [ ] Показывать content type в messages UI.
- [ ] Логировать multimodal errors.

## First Implementation Slice

Первый полезный срез для начала разработки:

1. `app/main.py` + `/api/health`.
2. `app/config.py`.
3. `.env.example`.
4. `README.md`.
5. PostgreSQL connection.
6. models: `bot_settings`, `prompt_versions`.
7. admin login.
8. `/prompts` page.

После этого можно подключать Telegram Bot Worker.
