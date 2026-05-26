# Roadmap: Telegram Bot Admin Panel

## Iteration 0: Project Foundation

Цель: подготовить каркас проекта и локальный запуск.

Результат:

- структура проекта;
- `.env.example`;
- README;
- FastAPI health endpoint;
- подключение PostgreSQL;
- базовые модели и миграции.

Критерий готовности:

- приложение запускается локально;
- `/api/health` возвращает OK;
- миграции применяются к PostgreSQL.

## Iteration 1: Admin Auth And Dashboard

Цель: сделать закрытую web-панель.

Результат:

- login/logout;
- cookie session;
- dashboard;
- счетчики пользователей, сообщений, ошибок;
- базовый CSS.

Критерий готовности:

- без входа закрытые страницы недоступны;
- админ входит по паролю из env;
- dashboard открывается после входа.

## Iteration 2: Prompt And Model Settings

Цель: дать администратору управление поведением бота.

Результат:

- страница prompt;
- сохранение новой версии prompt;
- страница model settings;
- audit log изменений;
- service layer для получения активных настроек.

Критерий готовности:

- admin меняет prompt/model settings из UI;
- активные настройки читаются из service layer;
- изменения пишутся в audit log.

## Iteration 3: Telegram Bot Integration

Цель: подключить Telegram-бота к настройкам из БД.

Результат:

- Telegram handlers;
- upsert Telegram user;
- получение active prompt/settings;
- вызов LLM adapter;
- отправка ответа пользователю;
- логирование inbound/outbound messages.

Критерий готовности:

- пользователь пишет боту;
- бот отвечает через выбранный provider;
- сообщения видны в admin panel.

## Iteration 4: Logs And Observability

Цель: сделать систему диагностируемой.

Результат:

- страница users;
- страница messages;
- страница errors;
- обработка ошибок интеграций;
- фильтры по дате/пользователю/типу.

Критерий готовности:

- admin видит пользователей;
- admin видит последние сообщения;
- ошибки сохраняются и отображаются.

## Iteration 5: Deploy

Цель: развернуть MVP в облако.

Результат:

- Railway service;
- Railway PostgreSQL;
- production env variables;
- README deploy section;
- smoke test после деплоя.

Критерий готовности:

- web-панель открывается в Railway;
- бот отвечает из облачного окружения;
- секреты заданы через Railway variables.

## Iteration 6: Optional Multimodal Extension

Цель: добавить функции из урока 3 после стабильного текстового MVP.

Возможности:

- voice transcription через faster-whisper или OpenAI Whisper;
- image analysis через vision model;
- включение/выключение multimodal функций из admin panel.

Критерий готовности:

- voice/image режимы не ломают базовый text flow;
- ошибки multimodal integrations видны в error logs.
