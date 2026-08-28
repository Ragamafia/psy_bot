from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.callbacks import NavCB
from app.config import get_settings
from app.content import texts
from app.keyboards.final import final_kb
from app.utils import render

router = Router(name="final")


@router.callback_query(NavCB.filter(F.to == "final"))
async def show_final(callback: CallbackQuery) -> None:
    psy = get_settings().psy
    await render(callback, texts.final(psy), final_kb(psy))
