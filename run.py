"""Entry point — starts the bot in long-polling mode."""
from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.database.base import init_models
from app.handlers import get_main_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger("bot")


async def main() -> None:
    if not settings.bot_token or "PASTE_YOUR_TOKEN" in settings.bot_token:
        log.error(
            "BOT_TOKEN is not set. Open the .env file and paste the token "
            "you got from @BotFather."
        )
        sys.exit(1)

    log.info("Database engine: %s", settings.db_engine)
    await init_models()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(get_main_router())

    log.info("Bot is starting (long polling)…")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped.")
