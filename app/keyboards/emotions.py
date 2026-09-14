"""Клавиатуры ветки «через эмоцию»."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callbacks import (
    EmotionCB,
    EmotionsDoneCB,
    EmotionToggleCB,
    HelpCB,
    MeaningCB,
)
from app.content.emotions import EMOTION_ORDER, EMOTIONS, HELP_BLOCK_TITLES
from app.keyboards.common import to_emotions, to_final, to_multi, to_zones

# Длинные подписи в два столбца переносятся на две строки и выглядят рвано —
# такие оттенки ставим по одному в ряд.
_WIDE_SHADE = 16


def emotions_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key in EMOTION_ORDER:
        builder.button(text=EMOTIONS[key].title, callback_data=EmotionCB(key=key))
    builder.adjust(2)
    builder.row(to_multi())
    builder.row(to_zones())
    return builder.as_markup()


def emotions_multi_kb(chosen: set[str]) -> InlineKeyboardMarkup:
    """Тот же список эмоций, но с галочками: повторное нажатие снимает выбор."""
    builder = InlineKeyboardBuilder()
    for key in EMOTION_ORDER:
        mark = "✅ " if key in chosen else ""
        builder.button(
            text=f"{mark}{EMOTIONS[key].title}",
            callback_data=EmotionToggleCB(key=key),
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text=f"Готово ({len(chosen)})" if chosen else "Готово",
            callback_data=EmotionsDoneCB().pack(),
        )
    )
    builder.row(to_emotions("← Выбрать одну эмоцию"))
    return builder.as_markup()


def shades_kb(emotion_key: str) -> InlineKeyboardMarkup:
    shades = EMOTIONS[emotion_key].shades
    builder = InlineKeyboardBuilder()
    for index, shade in enumerate(shades):
        builder.button(
            text=shade.title, callback_data=MeaningCB(emotion=emotion_key, shade=index)
        )
    builder.adjust(1 if any(len(s.title) > _WIDE_SHADE for s in shades) else 2)
    builder.row(to_emotions())
    return builder.as_markup()


def help_kb(emotion_key: str, shade_index: int | None = None) -> InlineKeyboardMarkup:
    """Список способов помощи — по фактически имеющемуся контенту: у грусти,
    радости и отвращения блока «Чтобы не сорваться» в таблице нет."""
    builder = InlineKeyboardBuilder()
    for block in EMOTIONS[emotion_key].help_blocks():
        builder.button(
            text=HELP_BLOCK_TITLES[block],
            callback_data=HelpCB(emotion=emotion_key, block=block, shade=shade_index),
        )
    builder.adjust(1)
    builder.row(to_final())
    builder.row(to_emotions())
    return builder.as_markup()


def help_block_kb(
    emotion_key: str, shade_index: int | None = None
) -> InlineKeyboardMarkup:
    """Экран одного способа помощи. Списка способов здесь нет намеренно:
    когда кнопки остаются на месте, подмена текста над ними незаметна."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="← Назад к способам помощи",
            callback_data=MeaningCB(emotion=emotion_key, shade=shade_index).pack(),
        )
    )
    builder.row(to_final())
    return builder.as_markup()
