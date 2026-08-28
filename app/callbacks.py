"""Фабрики callback_data.

Ключи везде латинские слаги, а не подписи кнопок: у callback_data
жёсткий лимит 64 байта, русский текст в него не влезает.
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class NavCB(CallbackData, prefix="nav"):
    # emotions | zones | final
    to: str
    # Для зон тела: сохранить уже отмеченные ощущения (переход между зонами)
    # или начать выбор заново (вход из списка эмоций).
    keep: bool = False


class EmotionCB(CallbackData, prefix="emo"):
    key: str


class ShadeCB(CallbackData, prefix="shade"):
    emotion: str
    index: int


class HelpCB(CallbackData, prefix="help"):
    emotion: str
    block: str


class ZoneCB(CallbackData, prefix="zone"):
    key: str


class SensationCB(CallbackData, prefix="sens"):
    key: str


class SensationsDoneCB(CallbackData, prefix="sdone"):
    pass


class AmbiguityCB(CallbackData, prefix="amb"):
    pair: str
    choice: str


class ResultCB(CallbackData, prefix="res"):
    """Эмоция, определённая по телу: сразу к значению и способам помощи,
    экран оттенков в этой ветке не нужен."""

    emotion: str
