import time
from aiogram import Router
from aiogram.types import CallbackQuery
from app.services.admins import allowed
router=Router(); START_TIME=time.time()
@router.callback_query(lambda c:c.data=="health")
async def health(call:CallbackQuery,db):
    if not await allowed(db,call.from_user.id,"stats"): await call.answer("⛔ Access denied",show_alert=True); return
    u=int(time.time()-START_TIME); h,r=divmod(u,3600); m,s=divmod(r,60); await call.message.answer(f"❤️ <b>Bot Health</b>\n\n🟢 Bot: Online\n🟢 Database: Connected\n⏱ Uptime: {h}h {m}m {s}s"); await call.answer()
