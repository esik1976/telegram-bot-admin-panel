# Requirements. Telegram Bot Admin Panel

## Роли пользователей

### Admin

Владелец или технический администратор Telegram-бота.

Может:

- входить в web-панель;
- смотреть dashboard;
- менять системный промпт;
- менять настройки моделей;
- смотреть пользователей;
- смотреть сообщения;
- смотреть ошибки;
- включать и выключать функции бота.

### Telegram User

Пользователь Telegram-бота.

Может:

- писать текстовые сообщения;
- отправлять голосовые сообщения;
- отправлять изображения;
- получать ответы от AI-бота.

### System

Фоновая часть приложения.

Отвечает за:

- получение сообщений от Telegram;
- вызов LLM/ASR/Vision;
- сохранение истории;
- применение актуальных настроек;
- логирование ошибок.

## User stories

### Admin

1. Как администратор, я хочу войти в web-панель, чтобы управлять ботом безопасно.
2. Как администратор, я хочу видеть статус бота, чтобы понимать, работает ли он.
3. Как администратор, я хочу менять системный промпт, чтобы адаптировать поведение бота без изменения кода.
4. Как администратор, я хочу менять модель для текстовых ответов, чтобы тестировать качество и стоимость.
5. Как администратор, я хочу видеть список пользователей Telegram, чтобы понимать аудиторию бота.
6. Как администратор, я хочу видеть историю сообщений, чтобы анализировать реальные сценарии использования.
7. Как администратор, я хочу видеть ошибки, чтобы быстрее диагностировать проблемы.
8. Как администратор, я хочу включать и выключать voice/image функции, чтобы управлять нагрузкой и расходами.

### Telegram User

1. Как пользователь Telegram, я хочу отправить текстовый вопрос, чтобы получить ответ от AI-бота.
2. Как пользователь Telegram, я хочу отправить голосовое сообщение, чтобы не печатать текст.
3. Как пользователь Telegram, я хочу отправить изображение, чтобы бот его проанализировал.
4. Как пользователь Telegram, я хочу получить понятную ошибку, если бот временно не может обработать запрос.

## Functional requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-001 | Admin can log in to web panel | Must | Admin opens login page, enters credentials, receives session, sees dashboard |
| FR-002 | Admin can see bot status dashboard | Must | Dashboard shows bot status, active model, enabled features, last error |
| FR-003 | Admin can edit system prompt | Must | Prompt can be changed in UI, saved to DB, and used by bot without code changes |
| FR-004 | Admin can configure text model | Must | Admin can set provider/model/base URL; bot uses saved config |
| FR-005 | Admin can enable/disable voice processing | Should | Toggle changes whether voice messages are processed |
| FR-006 | Admin can enable/disable image processing | Should | Toggle changes whether images are processed |
| FR-007 | System stores Telegram users | Must | On new message, user is created or updated in DB |
| FR-008 | System stores message history | Must | Incoming message and bot response are saved with timestamps |
| FR-009 | Admin can view recent messages | Must | UI shows paginated list of conversations/messages |
| FR-010 | System stores processing errors | Must | Errors are saved with type, message, timestamp, and context |
| FR-011 | Admin can view error log | Must | UI shows recent errors and details |
| FR-012 | Bot applies current settings from DB | Must | Changing prompt/model in admin panel affects future bot replies |
| FR-013 | Admin can update feature flags | Should | Text, voice, image, tools can be enabled/disabled |
| FR-014 | System exposes internal API for admin UI | Must | Frontend can fetch settings, users, messages, errors |
| FR-015 | Admin can log out | Must | Session is cleared and protected pages require login again |

## Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-001 | Local startup | Project can run locally with one documented command sequence |
| NFR-002 | Security | Secrets are stored in environment variables, not in Git |
| NFR-003 | Auth | Admin routes are protected by authentication |
| NFR-004 | Auditability | Changes to critical bot settings are timestamped |
| NFR-005 | Reliability | Bot should return user-friendly errors instead of crashing |
| NFR-006 | Maintainability | Backend, bot worker and frontend responsibilities are separated |
| NFR-007 | Observability | Errors and key processing events are logged |
| NFR-008 | Deployment | Project can be deployed to Railway or similar PaaS |

## Business rules

- Only authenticated admin can access web panel.
- Bot must read active settings from database before processing messages.
- If voice processing is disabled, bot replies that voice is temporarily unavailable.
- If image processing is disabled, bot replies that image analysis is temporarily unavailable.
- If LLM provider fails, error is saved and user receives a short fallback message.
- Admin password or auth secret must never be stored in plain text.
- Message history must not expose secret tokens or environment variables.

## Out of scope

- Multiple admin roles.
- Billing and payments.
- Team management.
- Manual operator chat.
- Advanced analytics dashboard.
- Token cost accounting.
- Multi-bot management.
- Prompt version comparison UI.
- GDPR-grade data deletion workflow.

## Open questions

- Нужна ли регистрация администратора или достаточно одного admin из `.env`?
- Нужно ли хранить полные ответы LLM или только metadata?
- Нужна ли интеграция с текущим локальным Ollama bot или сразу проектируем облачную версию?
- Нужно ли поддерживать несколько LLM providers в MVP?
- Нужно ли показывать медиафайлы в админке или только metadata?
