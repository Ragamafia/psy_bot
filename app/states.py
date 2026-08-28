from aiogram.fsm.state import State, StatesGroup


class BodyFlow(StatesGroup):
    """Телесный вход. Хендлеры по состоянию не фильтруются — оно нужно только
    как маркер; сам выбор лежит в data (`selected`, `answers`)."""

    selecting = State()
    disambiguating = State()
