from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.callbacks import AmbiguityCB, NavCB, ResultCB, SensationCB, SensationsDoneCB, ZoneCB
from app.content import texts
from app.content.body import AMBIGUITY_QUESTIONS, SENSATIONS, ZONES_BY_KEY
from app.handlers.emotions import meaning_view, results_view
from app.keyboards.body import ambiguity_kb, sensations_kb, zones_kb
from app.services.resolver import Resolution, resolve
from app.states import BodyFlow
from app.utils import lower_first, render

router = Router(name="body")


async def _reset(state: FSMContext) -> None:
    await state.set_state(BodyFlow.selecting)
    await state.update_data(selected=[], answers={}, zone=None)


def _sensations_view(
    zone_key: str, selected: set[str]
) -> tuple[str, InlineKeyboardMarkup]:
    """Экран выбора ощущений. Когда что-то уже отмечено — просим посмотреть
    и другие зоны: по одному признаку эмоция определяется плохо."""
    zone = ZONES_BY_KEY[zone_key]
    if not selected:
        text = texts.CHOOSE_SENSATIONS.format(zone=zone.title)
    else:
        labels = [
            lower_first(SENSATIONS[key].label)
            for key in sorted(selected)
            if key in SENSATIONS
        ]
        text = texts.CHOOSE_SENSATIONS_MORE.format(
            zone=zone.title, selected=", ".join(labels)
        )
    return text, sensations_kb(zone_key, selected)


@router.callback_query(NavCB.filter(F.to == "zones"))
async def show_zones(callback: CallbackQuery, callback_data: NavCB, state: FSMContext) -> None:
    # keep=True — переход между зонами, отмеченное сохраняем.
    if not callback_data.keep:
        await _reset(state)
    await render(callback, texts.CHOOSE_ZONE, zones_kb())


@router.callback_query(ZoneCB.filter())
async def show_sensations(callback: CallbackQuery, callback_data: ZoneCB, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(BodyFlow.selecting)
    await state.update_data(zone=callback_data.key)

    await render(
        callback,
        *_sensations_view(callback_data.key, set(data.get("selected", []))),
    )


@router.callback_query(SensationCB.filter())
async def toggle_sensation(
    callback: CallbackQuery, callback_data: SensationCB, state: FSMContext
) -> None:
    data = await state.get_data()
    zone_key = data.get("zone")

    # Состояние живёт в памяти: после рестарта бота старые кнопки его не найдут.
    if zone_key not in ZONES_BY_KEY:
        await _reset(state)
        await render(callback, texts.CHOOSE_ZONE, zones_kb())
        return

    selected = set(data.get("selected", []))
    selected.symmetric_difference_update({callback_data.key})
    await state.update_data(selected=sorted(selected))

    await render(callback, *_sensations_view(zone_key, selected))


@router.callback_query(SensationsDoneCB.filter())
async def finish_selection(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected = list(data.get("selected", []))
    if not selected:
        await callback.answer(texts.NOTHING_SELECTED, show_alert=True)
        return
    await _advance(callback, state, selected, dict(data.get("answers", {})))


@router.callback_query(AmbiguityCB.filter())
async def answer_ambiguity(
    callback: CallbackQuery, callback_data: AmbiguityCB, state: FSMContext
) -> None:
    data = await state.get_data()
    selected = list(data.get("selected", []))
    if not selected:
        await _reset(state)
        await render(callback, texts.CHOOSE_ZONE, zones_kb())
        return

    answers = dict(data.get("answers", {}))
    answers[callback_data.pair] = callback_data.choice
    await state.update_data(answers=answers)

    await _advance(callback, state, selected, answers)


@router.callback_query(ResultCB.filter())
async def help_for_result(callback: CallbackQuery, callback_data: ResultCB) -> None:
    await render(callback, *meaning_view(callback_data.emotion))


async def _advance(
    callback: CallbackQuery,
    state: FSMContext,
    selected: list[str],
    answers: dict[str, str],
) -> None:
    """Либо задаёт очередной уточняющий вопрос, либо показывает результат."""
    resolution = resolve(selected, answers)

    if resolution.needs_question:
        pair = resolution.pending[0]
        await state.set_state(BodyFlow.disambiguating)
        await render(callback, AMBIGUITY_QUESTIONS[pair], ambiguity_kb(pair))
        return

    await _show_results(callback, resolution)


async def _show_results(callback: CallbackQuery, resolution: Resolution) -> None:
    if not resolution.emotions:
        await render(callback, texts.CHOOSE_ZONE, zones_kb())
        return

    await render(
        callback, *results_view(resolution.emotions, resolution.truncated)
    )
