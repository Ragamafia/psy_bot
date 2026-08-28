from aiogram import Router

from app.handlers import body, emotions, final, start

router = Router(name="root")
router.include_routers(start.router, emotions.router, body.router, final.router)
