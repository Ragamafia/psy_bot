from __future__ import annotations

from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def render(
    callback: CallbackQuery,
    text: str,
    markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Перерисовывает текущий экран вместо отправки нового сообщения    """
    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=markup)


def lower_first(text: str) -> str:
    """«Ваши границы нарушены» → «ваши границы нарушены» для вставки после тире."""
    return text[:1].lower() + text[1:] if text else text


def join_titles(titles: list[str]) -> str:
    """['Злость', 'Грусть'] → 'Злость и Грусть'."""
    if len(titles) <= 1:
        return "".join(titles)
    return f"{', '.join(titles[:-1])} и {titles[-1]}"
