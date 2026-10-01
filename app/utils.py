from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    Message,
    User,
)

from app.logger import logger

# Файл загружается в Telegram один раз, дальше шлём по file_id.
# Ключ — путь к файлу или имя нарисованной карточки.
_photo_ids: dict[Path | str, str] = {}


async def render(
    callback: CallbackQuery,
    text: str,
    markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Перерисовывает текущий экран вместо отправки нового сообщения"""
    await callback.answer()
    message = callback.message
    if not isinstance(message, Message):
        return
    # Сообщение с фото нельзя превратить в текстовое — заменяем его новым.
    if message.photo:
        await _delete(message)
        await message.answer(text, reply_markup=markup)
        return
    with suppress(TelegramBadRequest):
        await message.edit_text(text, reply_markup=markup)


async def render_photo(
    callback: CallbackQuery,
    photo: Path,
    caption: str,
    markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Экран с фото: текстовое сообщение удаляем и присылаем фото с подписью."""
    if not photo.is_file():
        logger.warning(f"Фото не найдено: {photo}")
        await render(callback, caption, markup)
        return

    await _send_photo(callback, photo, _photo_ids.get(photo) or FSInputFile(photo), caption, markup)


async def render_card(
    callback: CallbackQuery,
    key: str,
    draw: Callable[[], bytes | None],
    caption: str,
    fallback: str,
    markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Экран с нарисованной картинкой. Рисуем только до первой отправки,
    дальше шлём по file_id. Не нарисовалась — показываем fallback текстом."""
    photo: str | BufferedInputFile | None = _photo_ids.get(key)
    if photo is None:
        # Pillow работает синхронно — уводим из цикла событий.
        image = await asyncio.to_thread(draw)
        if image is None:
            await render(callback, fallback, markup)
            return
        photo = BufferedInputFile(image, filename=f"{key}.jpg")
    await _send_photo(callback, key, photo, caption, markup)


async def _send_photo(
    callback: CallbackQuery,
    key: Path | str,
    photo: str | FSInputFile | BufferedInputFile,
    caption: str,
    markup: InlineKeyboardMarkup | None,
) -> None:
    """Текущее сообщение удаляем и присылаем фото с подписью."""
    await callback.answer()
    message = callback.message
    if not isinstance(message, Message):
        return
    await _delete(message)

    sent = await message.answer_photo(photo, caption=caption, reply_markup=markup)
    if sent.photo:
        _photo_ids[key] = sent.photo[-1].file_id


async def _delete(message: Message) -> None:
    # Сообщения старше 48 часов Telegram удалить не даёт — тогда просто оставляем.
    with suppress(TelegramBadRequest):
        await message.delete()


def user_label(user: User | None) -> str:
    """Кто нажал — для лога: id и @username, если он есть."""
    if user is None:
        return "unknown"
    return f"{user.id} @{user.username}" if user.username else str(user.id)


def lower_first(text: str) -> str:
    """«Ваши границы нарушены» → «ваши границы нарушены» для вставки после тире."""
    return text[:1].lower() + text[1:] if text else text


def join_titles(titles: list[str]) -> str:
    """['Злость', 'Грусть'] → 'Злость и Грусть'."""
    if len(titles) <= 1:
        return "".join(titles)
    return f"{', '.join(titles[:-1])} и {titles[-1]}"
