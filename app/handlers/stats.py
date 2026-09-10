from aiogram import Router
from aiogram.types import CallbackQuery
from app.services.admins import allowed
router=Router()
@router.callback_query(lambda c:c.data=="users:stats")
async def stats(call:CallbackQuery,db):
    if not await allowed(db,call.from_user.id,"stats"): await call.answer("⛔ Access denied",show_alert=True); return
    s=await db.stats(); await call.message.answer("📊 <b>Statistics</b>\n\n"+"\n".join([f"👥 Users: <b>{s['users']}</b>",f"🆕 New requests: <b>{s['new_requests']}</b>",f"🕐 Old requests: <b>{s['old_requests']}</b>",f"✅ Accepted: <b>{s['accepted']}</b>",f"⏳ Pending: <b>{s['pending']}</b>",f"📨 DMs sent: <b>{s['dm_sent']}</b>",f"⚠️ DMs failed: <b>{s['dm_failed']}</b>",f"⏰ Scheduled: <b>{s['scheduled']}</b>"])); await call.answer()
