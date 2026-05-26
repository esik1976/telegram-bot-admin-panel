import logging

from telegram import Update
from telegram.request import HTTPXRequest
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import get_settings
from app.db import SessionLocal
from app.llm import generate_answer
from app.services.errors import log_error
from app.services.messages import log_message
from app.services.settings import get_active_prompt, get_active_settings
from app.services.users import upsert_telegram_user

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_text("Привет. Я AI-бот с web-админкой. Напиши вопрос.")


async def answer_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None or not update.message.text:
        return

    app_settings = get_settings()
    telegram_user = None

    try:
        await update.message.chat.send_action("typing")

        with SessionLocal() as db:
            telegram_user = upsert_telegram_user(
                db,
                telegram_id=update.effective_user.id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                language_code=update.effective_user.language_code,
            )
            log_message(
                db,
                telegram_user=telegram_user,
                direction="inbound",
                content=update.message.text,
            )
            prompt = get_active_prompt(db)
            bot_settings = get_active_settings(db)

            answer = await generate_answer(
                user_message=update.message.text,
                system_prompt=prompt.content,
                bot_settings=bot_settings,
                app_settings=app_settings,
            )

            log_message(
                db,
                telegram_user=telegram_user,
                direction="outbound",
                content=answer,
                provider=bot_settings.provider,
                model=bot_settings.model,
            )
            db.commit()

        await update.message.reply_text(answer)
    except Exception as exc:
        logger.exception("Bot message processing failed")
        with SessionLocal() as db:
            log_error(db, source="bot", error=exc, telegram_user=telegram_user)
            db.commit()
        await update.message.reply_text("Не смог обработать сообщение. Ошибка сохранена в журнале.")


def build_application() -> Application:
    settings = get_settings()
    if not settings.telegram_bot_token or settings.telegram_bot_token == "change-me":
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env before starting bot worker")

    request = HTTPXRequest(
        connect_timeout=20,
        read_timeout=30,
        write_timeout=30,
        httpx_kwargs={"verify": settings.http_ssl_verify},
    )
    get_updates_request = HTTPXRequest(
        connect_timeout=20,
        read_timeout=30,
        write_timeout=30,
        httpx_kwargs={"verify": settings.http_ssl_verify},
    )
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_text))
    return application


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    application = build_application()
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
