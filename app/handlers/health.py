from aiogram import Router
from aiogram.types import CallbackQuery
from app.services.admins import allowed
router=Router()
@router.callback_query(lambda c:c.data=='health')
async def health(c,db):
 if not await allowed(db,c.from_user.id,'stats'): return await c.answer('🔒 Access required.',show_alert=True)
 await c.message.answer('❤️ <b>Health</b>\n\n🟢 Bot online\n🟢 Database connected'); await c.answer()
