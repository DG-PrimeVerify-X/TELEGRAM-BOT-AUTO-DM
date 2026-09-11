from aiogram import Router
from aiogram.types import CallbackQuery
from app.services.admins import allowed
router=Router()
@router.callback_query(lambda c:c.data=='users:stats')
async def stats(c,db):
 if not await allowed(db,c.from_user.id,'stats'): return await c.answer('🔒 Access required.',show_alert=True)
 s=await db.stats(); await c.message.answer('📊 <b>Statistics</b>\n\n👥 Users: %s\n📨 Requests: %s\n✅ Accepted: %s\n🕐 Pending: %s\n🤖 DM sent: %s\n⚠️ DM failed: %s\n⏰ Scheduled: %s'%tuple(s[k] for k in ['users','requests','accepted','pending','dm_sent','dm_failed','scheduled'])); await c.answer()
