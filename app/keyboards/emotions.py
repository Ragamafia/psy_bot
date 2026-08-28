"""Клавиатуры ветки «через эмоцию»."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callbacks import EmotionCB, HelpCB, ShadeCB
from app.content.emotions import EMOTION_ORDER, EMOTIONS, HELP_BLOCK_TITLES
from app.keyboards.common import to_emotions, to_final, to_zones


def emotions_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key in EMOTION_ORDER:
        builder.button(text=EMOTIONS[key].title, callback_data=EmotionCB(key=key))
    builder.adjust(2)
    builder.row(to_zones())
    return builder.as_markup()


def shades_kb(emotion_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, shade in enumerate(EMOTIONS[emotion_key].shades):
        builder.button(text=shade, callback_data=ShadeCB(emotion=emotion_key, index=index))
    builder.adjust(2)
    builder.row(to_emotions())
    return builder.as_markup()


def help_kb(emotion_key: str) -> InlineKeyboardMarkup:
    """Кнопки самопомощи — по фактически имеющемуся контенту: у грусти,
    радости и отвращения блока «Чтобы не сорваться» в таблице нет."""
    builder = InlineKeyboardBuilder()
    for block in EMOTIONS[emotion_key].help_blocks():
        builder.button(
            text=HELP_BLOCK_TITLES[block],
            callback_data=HelpCB(emotion=emotion_key, block=block),
        )
    builder.adjust(1)
    builder.row(to_final())
    builder.row(to_emotions())
    return builder.as_markup()
