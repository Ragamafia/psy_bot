"""Фабрики callback_data.

Ключи везде латинские слаги, а не подписи кнопок: у callback_data
жёсткий лимит 64 байта, русский текст в него не влезает.
"""

from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class NavCB(CallbackData, prefix="nav"):
    # emotions | emotions_multi | zones | final
    to: str
    # Для зон тела: сохранить уже отмеченные ощущения (переход между зонами)
    # или начать выбор заново (вход из списка эмоций).
    keep: bool = False


class EmotionCB(CallbackData, prefix="emo"):
    key: str


class EmotionToggleCB(CallbackData, prefix="emotog"):
    """Отметить/снять эмоцию, когда человек выбирает несколько сразу."""

    key: str


class EmotionsDoneCB(CallbackData, prefix="emodone"):
    pass


class MeaningCB(CallbackData, prefix="mean"):
    """Экран «что показывает эмоция» со списком способов помощи.

    Сюда ведут три дороги: выбор оттенка, эмоция, определённая по телу,
    и кнопка «Назад» из конкретного способа помощи.
    """

    emotion: str
    # Индекс оттенка или None, если эмоцию выбрали без оттенка.
    shade: int | None = None


class HelpCB(CallbackData, prefix="help"):
    emotion: str
    block: str
    # Оттенок, с которого пришли, — чтобы «Назад» вернуло на тот же экран.
    shade: int | None = None


class ZoneCB(CallbackData, prefix="zone"):
    key: str


class SensationCB(CallbackData, prefix="sens"):
    key: str


class SensationsDoneCB(CallbackData, prefix="sdone"):
    pass


class AmbiguityCB(CallbackData, prefix="amb"):
    pair: str
    choice: str
