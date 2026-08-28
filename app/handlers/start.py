from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.callbacks import NavCB
from app.content import texts
from app.keyboards.emotions import emotions_kb
from app.utils import render

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.START, reply_markup=emotions_kb())


@router.callback_query(NavCB.filter(F.to == "emotions"))
async def show_emotions(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await render(callback, texts.CHOOSE_EMOTION, emotions_kb())
