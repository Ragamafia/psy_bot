from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.callbacks import EmotionCB, HelpCB, ShadeCB
from app.content import texts
from app.content.emotions import EMOTIONS, HELP_BLOCK_TITLES
from app.keyboards.emotions import help_kb, shades_kb
from app.utils import render

router = Router(name="emotions")


def meaning_view(emotion_key: str, shade: str | None = None) -> tuple[str, InlineKeyboardMarkup]:
    """Экран «что показывает эмоция» + кнопки самопомощи    """
    emotion = EMOTIONS[emotion_key]
    template = texts.MEANING_WITH_SHADE if shade else texts.MEANING
    text = template.format(emotion=emotion.title, shade=shade, meaning=emotion.meaning)
    return text, help_kb(emotion_key)


@router.callback_query(EmotionCB.filter())
async def choose_emotion(callback: CallbackQuery, callback_data: EmotionCB) -> None:
    emotion = EMOTIONS[callback_data.key]

    # У обиды оттенков в таблице нет — экран пропускаем.
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
    emotion = EMOTIONS[callback_data.emotion]
    shade = emotion.shades[callback_data.index]
    await render(callback, *meaning_view(emotion.key, shade))


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
