from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.callbacks import AmbiguityCB, NavCB, ResultCB, SensationCB, SensationsDoneCB, ZoneCB
from app.content import texts
from app.content.body import AMBIGUITY_QUESTIONS, ZONES_BY_KEY
from app.content.emotions import EMOTIONS
from app.handlers.emotions import meaning_view
from app.keyboards.body import ambiguity_kb, results_kb, sensations_kb, zones_kb
from app.keyboards.emotions import help_kb
from app.services.resolver import Resolution, resolve
from app.states import BodyFlow
from app.utils import join_titles, lower_first, render

router = Router(name="body")


async def _reset(state: FSMContext) -> None:
    await state.set_state(BodyFlow.selecting)
    await state.update_data(selected=[], answers={}, zone=None)


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

    zone = ZONES_BY_KEY[callback_data.key]
    await render(
        callback,
        texts.CHOOSE_SENSATIONS.format(zone=zone.title),
        sensations_kb(zone.key, set(data.get("selected", []))),
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

    await render(
        callback,
        texts.CHOOSE_SENSATIONS.format(zone=ZONES_BY_KEY[zone_key].title),
        sensations_kb(zone_key, selected),
    )


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
    keys = resolution.emotions
    if not keys:
        await render(callback, texts.CHOOSE_ZONE, zones_kb())
        return

    if len(keys) == 1:
        emotion = EMOTIONS[keys[0]]
        text = texts.RESULT_SINGLE.format(emotion=emotion.title, meaning=emotion.meaning)
        await render(callback, text, help_kb(emotion.key))
        return

    titles = join_titles([f"<b>{EMOTIONS[key].title}</b>" for key in keys])
    lines = [texts.RESULT_MANY_HEADER.format(emotions=titles), ""]
    lines += [
        f"▸ <b>{EMOTIONS[key].title}</b> — {lower_first(EMOTIONS[key].meaning)}"
        for key in keys
    ]
    if resolution.truncated:
        lines += ["", texts.RESULT_TRUNCATED]
    lines += ["", texts.RESULT_MANY_FOOTER]

    await render(callback, "\n".join(lines), results_kb(keys))
