"""Уведомления владельцам бота о действиях пользователей"""

from __future__ import annotations

from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import User

from app.config import get_settings
from app.logger import logger


async def notify(bot: Bot | None, text: str) -> None:
    """Шлёт текст каждому из NOTIFY_IDS. Ошибка отправки только пишется в лог —
    пользователь от неё страдать не должен."""
    if bot is None:
        return
    for chat_id in get_settings().notify.ids:
        try:
            await bot.send_message(chat_id, text)
        except TelegramAPIError as error:
            # Чаще всего Forbidden: получатель ни разу не нажимал /start в боте.
            logger.warning(f"Уведомление для {chat_id} не отправлено: {error}")


def user_mention(user: User | None) -> str:
    """Имя и @username со ссылкой на профиль; если нет ни того ни другого — id."""
    if user is None:
        return "unknown"
    parts = []
    if user.full_name:
        parts.append(escape(user.full_name))
    if user.username:
        parts.append(f"@{user.username}")
    if len(parts) == 2:
        label = f"{parts[0]} ({parts[1]})"
    else:
        label = parts[0] if parts else str(user.id)
    return f'<a href="tg://user?id={user.id}">{label}</a>'
