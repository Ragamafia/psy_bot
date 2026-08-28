"""Кнопки, которые повторяются на разных экранах."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton

from app.callbacks import NavCB


def to_emotions(text: str = "← К списку эмоций") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=NavCB(to="emotions").pack())


def to_zones(
    text: str = "Затрудняюсь назвать эмоцию", keep: bool = False
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text, callback_data=NavCB(to="zones", keep=keep).pack()
    )


def to_final(text: str = "Записаться на сеанс") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=NavCB(to="final").pack())
