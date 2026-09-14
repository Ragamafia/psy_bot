"""Клавиатуры телесного входа."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callbacks import (
    AmbiguityCB,
    MeaningCB,
    SensationCB,
    SensationsDoneCB,
    ZoneCB,
)
from app.content.body import ZONES, ZONES_BY_KEY
from app.content.emotions import EMOTIONS
from app.keyboards.common import to_emotions, to_final, to_zones


def _done_button(count: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=f"Готово ({count})" if count else "Готово",
        callback_data=SensationsDoneCB().pack(),
    )


def zones_kb(selected: set[str] = frozenset()) -> InlineKeyboardMarkup:
    """Зоны с отметками: сколько ощущений уже выбрано в каждой. Иначе, выйдя
    из зоны, человек теряет из виду весь набор."""
    builder = InlineKeyboardBuilder()
    for zone in ZONES:
        count = sum(1 for s in zone.sensations if s.key in selected)
        title = f"✅ {zone.title} · {count}" if count else zone.title
        builder.button(text=title, callback_data=ZoneCB(key=zone.key))
    builder.adjust(1)
    # Завершить выбор можно прямо отсюда, не заходя обратно в зону.
    if selected:
        builder.row(_done_button(len(selected)))
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
        _done_button(len(selected)),
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
            callback_data=MeaningCB(emotion=key),
        )
    builder.adjust(1)
    builder.row(to_final())
    builder.row(to_emotions())
    return builder.as_markup()
