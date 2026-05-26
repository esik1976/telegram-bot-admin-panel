# ADR-001: Modular Monolith For MVP

## Status

Accepted

## Context

Проект `Telegram Bot Admin Panel` должен быть учебным fullstack MVP: Telegram-бот + web-админка + PostgreSQL + деплой в Railway.

Система содержит несколько логических частей:

- Telegram Bot Worker;
- FastAPI Backend;
- Admin Web UI;
- Service Layer;
- PostgreSQL;
- LLM Adapter.

Можно реализовать их как отдельные сервисы, но это увеличит сложность запуска, деплоя, конфигурации и отладки.

## Decision

Для MVP выбираем модульный монолит:

- один репозиторий;
- один Python-проект;
- общий `Service Layer`;
- FastAPI routes и Telegram handlers в разных модулях;
- одна PostgreSQL база;
- один Railway service на первом этапе.

Внутри проекта сохраняем границы модулей, чтобы позже можно было вынести Bot Worker в отдельный процесс.

## Consequences

### Positive

- Проще локально запустить и проверить.
- Меньше инфраструктуры для учебного проекта.
- Быстрее получить работающий MVP.
- Web UI и Bot Worker используют общую бизнес-логику.
- Проще поддерживать документацию и onboarding.

### Negative

- Один процесс может стать узким местом при росте нагрузки.
- Ошибка в worker может повлиять на web-приложение, если не изолировать обработку.
- Горизонтальное масштабирование будет сложнее, чем при разделенных сервисах.

### Mitigation

- Держать `bot_worker`, `web`, `api`, `services`, `db` отдельными модулями.
- Не размещать SQL-запросы напрямую в Telegram handlers.
- Логировать ошибки worker в `error_logs`.
- Позже можно вынести worker в отдельный Railway service без переписывания service layer.

## Alternatives Considered

### Separate backend and bot services

Плюсы:

- лучше изоляция;
- проще масштабировать worker отдельно.

Минусы:

- больше переменных окружения;
- нужно проектировать internal API;
- сложнее учебный запуск;
- больше мест для ошибок.

### Frontend SPA + API

Плюсы:

- современный frontend workflow;
- удобнее строить сложный UI.

Минусы:

- нужен build pipeline;
- больше зависимостей;
- MVP админки можно закрыть server-rendered HTML.

## Decision Date

2026-05-24
