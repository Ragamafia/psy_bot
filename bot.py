from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils.token import TokenValidationError
from app.logger import logger

from app.config import get_settings
from app.handlers import router


BAD_TOKEN = "Токен не принят Telegram. Проверьте BOT_TOKEN."


async def run(bot: Bot) -> None:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)

    await bot.set_my_commands([BotCommand(command="start", description="Начать заново")])
    await bot.delete_webhook(drop_pending_updates=True)

    me = await bot.get_me()
    logger.success(f"BOT STARTED: {me.username}")
    await dispatcher.start_polling(bot)


async def main() -> None:
    settings = get_settings()
    try:
        bot = Bot(
            token=settings.bot.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    except TokenValidationError:
        logger.error(BAD_TOKEN)
        return

    # Контекстный менеджер закрывает сессию и при падении на старте.
    async with bot:
        try:
            await run(bot)
        except TelegramUnauthorizedError:
            logger.error(BAD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("STOP")
