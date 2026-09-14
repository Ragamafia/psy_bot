from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.callbacks import (
    EmotionCB,
    EmotionsDoneCB,
    EmotionToggleCB,
    HelpCB,
    NavCB,
    ShadeCB,
)
from app.content import texts
from app.content.emotions import EMOTION_ORDER, EMOTIONS, HELP_BLOCK_TITLES
from app.keyboards.body import results_kb
from app.keyboards.emotions import emotions_multi_kb, help_kb, shades_kb
from app.states import EmotionFlow
from app.utils import join_titles, lower_first, render

router = Router(name="emotions")


def meaning_view(emotion_key: str, shade_index: int | None = None) -> tuple[str, InlineKeyboardMarkup]:
    """Экран «что показывает эмоция» + кнопки самопомощи."""
    emotion = EMOTIONS[emotion_key]
    if shade_index is None:
        text = texts.MEANING.format(emotion=emotion.title, meaning=emotion.meaning)
        return text, help_kb(emotion_key)

    shade = emotion.shades[shade_index]
    template = texts.MEANING_WITH_SHADE_NOTE if shade.note else texts.MEANING_WITH_SHADE
    text = template.format(
        emotion=emotion.title,
        shade=lower_first(shade.title),
        note=shade.note,
        meaning=emotion.meaning,
    )
    return text, help_kb(emotion_key)


def results_view(
    emotion_keys: list[str], truncated: int = 0, inferred: bool = True
) -> tuple[str, InlineKeyboardMarkup]:
    """Экран с несколькими эмоциями: определёнными по телу или выбранными вручную."""
    if len(emotion_keys) == 1:
        emotion = EMOTIONS[emotion_keys[0]]
        text = texts.RESULT_SINGLE.format(emotion=emotion.title, meaning=emotion.meaning)
        return text, help_kb(emotion.key)

    titles = join_titles([f"<b>{EMOTIONS[key].title}</b>" for key in emotion_keys])
    header = texts.RESULT_MANY_HEADER if inferred else texts.CHOSEN_MANY_HEADER
    lines = [header.format(emotions=titles), ""]
    lines += [
        f"▸ <b>{EMOTIONS[key].title}</b> — {lower_first(EMOTIONS[key].meaning)}"
        for key in emotion_keys
    ]
    if truncated:
        lines += ["", texts.RESULT_TRUNCATED]
    lines += ["", texts.RESULT_MANY_FOOTER]

    return "\n".join(lines), results_kb(emotion_keys)


@router.callback_query(EmotionCB.filter())
async def choose_emotion(callback: CallbackQuery, callback_data: EmotionCB) -> None:
    emotion = EMOTIONS[callback_data.key]

    if not emotion.shades:
        await render(callback, *meaning_view(emotion.key))
        return

    await render(
        callback,
        texts.CHOOSE_SHADE.format(emotion=emotion.title),
        shades_kb(emotion.key),
    )


@router.callback_query(ShadeCB.filter())
async def choose_shade(callback: CallbackQuery, callback_data: ShadeCB) -> None:
    await render(callback, *meaning_view(callback_data.emotion, callback_data.index))


@router.callback_query(NavCB.filter(F.to == "emotions_multi"))
async def show_emotions_multi(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EmotionFlow.choosing_many)
    await state.update_data(chosen=[])
    await render(callback, texts.CHOOSE_EMOTIONS_MULTI, emotions_multi_kb(set()))


@router.callback_query(EmotionToggleCB.filter())
async def toggle_emotion(
    callback: CallbackQuery, callback_data: EmotionToggleCB, state: FSMContext
) -> None:
    data = await state.get_data()
    chosen = set(data.get("chosen", []))
    chosen.symmetric_difference_update({callback_data.key})
    await state.update_data(chosen=sorted(chosen))

    await render(callback, texts.CHOOSE_EMOTIONS_MULTI, emotions_multi_kb(chosen))


@router.callback_query(EmotionsDoneCB.filter())
async def finish_emotions(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    # Порядок как в списке эмоций, а не как человек нажимал.
    chosen = [key for key in EMOTION_ORDER if key in set(data.get("chosen", []))]

    if not chosen:
        await callback.answer(texts.NO_EMOTION_SELECTED, show_alert=True)
        return

    # Одна эмоция — это обычный выбор, ведём через оттенки как из общего списка.
    if len(chosen) == 1:
        await state.clear()
        await choose_emotion(callback, EmotionCB(key=chosen[0]))
        return

    await state.clear()
    await render(callback, *results_view(chosen, inferred=False))


@router.callback_query(HelpCB.filter())
async def show_help_block(callback: CallbackQuery, callback_data: HelpCB) -> None:
    emotion = EMOTIONS[callback_data.emotion]
    text = texts.HELP_BLOCK.format(
        emotion=emotion.title,
        block=HELP_BLOCK_TITLES[callback_data.block],
        text=emotion.help[callback_data.block],
    )
    # Клавиатура та же — можно сразу перейти к другому способу.
    await render(callback, text, help_kb(emotion.key))
