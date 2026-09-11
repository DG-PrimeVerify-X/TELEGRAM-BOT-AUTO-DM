from aiogram import Router
from aiogram.types import CallbackQuery
from app.services.admins import allowed
router=Router()
@router.callback_query(lambda c:c.data=='backup')
async def backup(c,db):
 if not await allowed(db,c.from_user.id,'backup'): return await c.answer('🔒 Access required.',show_alert=True)
 await c.message.answer('💾 Backup is stored in the VPS database file.\nUse the VPS deploy/update backup command before upgrades.'); await c.answer()
