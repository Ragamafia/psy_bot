from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.config import PsychologistSettings
from app.keyboards.common import to_emotions


def final_kb(psy: PsychologistSettings) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Написать в Telegram", url=psy.tg_link))
    builder.row(to_emotions("← Вернуться к эмоциям"))
    return builder.as_markup()
