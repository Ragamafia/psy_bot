from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.callbacks import NavCB
from app.config import get_settings
from app.content import texts
from app.keyboards.final import final_kb
from app.logger import logger
from app.utils import render_photo, user_label

router = Router(name="final")


@router.callback_query(NavCB.filter(F.to == "final"))
async def show_final(callback: CallbackQuery) -> None:
    logger.info(f"SIGN UP: {user_label(callback.from_user)}")
    psy = get_settings().psy
    await render_photo(callback, psy.photo_path, texts.final(psy), final_kb(psy))
