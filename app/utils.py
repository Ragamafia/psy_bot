from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, Message, User

from app.logger import logger

# Файл загружается в Telegram один раз, дальше шлём по file_id.
_photo_ids: dict[Path, str] = {}


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

    await callback.answer()
    message = callback.message
    if not isinstance(message, Message):
        return
    await _delete(message)

    sent = await message.answer_photo(
        _photo_ids.get(photo) or FSInputFile(photo),
        caption=caption,
        reply_markup=markup,
    )
    if sent.photo:
        _photo_ids[photo] = sent.photo[-1].file_id


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
