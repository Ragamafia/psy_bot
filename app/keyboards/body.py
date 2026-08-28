"""Клавиатуры телесного входа."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callbacks import AmbiguityCB, ResultCB, SensationCB, SensationsDoneCB, ZoneCB
from app.content.body import ZONES, ZONES_BY_KEY
from app.content.emotions import EMOTIONS
from app.keyboards.common import to_emotions, to_final, to_zones


def zones_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for zone in ZONES:
        builder.button(text=zone.title, callback_data=ZoneCB(key=zone.key))
    builder.adjust(1)
    builder.row(to_emotions())
    return builder.as_markup()


def sensations_kb(zone_key: str, selected: set[str]) -> InlineKeyboardMarkup:
    """Мультивыбор внутри зоны: отмеченное помечается галочкой,
    повторное нажатие снимает выбор."""
    builder = InlineKeyboardBuilder()
    for sensation in ZONES_BY_KEY[zone_key].sensations:
        mark = "✅ " if sensation.key in selected else ""
        builder.button(
            text=f"{mark}{sensation.label}",
            callback_data=SensationCB(key=sensation.key),
        )
    builder.adjust(1)
    builder.row(
        to_zones("← Другая зона тела", keep=True),
        InlineKeyboardButton(
            text=f"Готово ({len(selected)})" if selected else "Готово",
            callback_data=SensationsDoneCB().pack(),
        ),
    )
    return builder.as_markup()


def ambiguity_kb(pair: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key in pair.split("-"):
        builder.button(
            text=EMOTIONS[key].title,
            callback_data=AmbiguityCB(pair=pair, choice=key),
        )
    builder.adjust(2)
    builder.row(to_zones("← Изменить выбор ощущений", keep=True))
    return builder.as_markup()


def results_kb(emotion_keys: list[str]) -> InlineKeyboardMarkup:
    """Выбор, с какой из найденных эмоций работать."""
    builder = InlineKeyboardBuilder()
    for key in emotion_keys:
        builder.button(
            text=f"Помочь {EMOTIONS[key].instrumental}",
            callback_data=ResultCB(emotion=key),
        )
    builder.adjust(1)
    builder.row(to_final())
    builder.row(to_emotions())
    return builder.as_markup()
