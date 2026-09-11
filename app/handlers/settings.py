from aiogram import Router
from aiogram.types import CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton,Message
from aiogram.filters import Command
from app.services.admins import allowed
router=Router()
@router.callback_query(lambda c:c.data in {'settings','set:dm','set:accept'})
async def settings(call,db):
 if not await allowed(db,call.from_user.id,'settings'): return await call.answer('🔒 Access required.',show_alert=True)
 if call.data=='settings':
  m=await db.get_setting('maintenance','0'); await call.message.answer(f'⚙️ <b>Global Settings</b>\nMaintenance: {"🟢 ON" if m=="1" else "🔴 OFF"}\n\nUse /maintenance to toggle.\nUse /ownerusername USERNAME to change Contact Owner.')
 else:
  key='auto_dm' if call.data=='set:dm' else 'auto_accept'; v=await db.get_setting(key,'0'); await db.set_setting(key,'0' if v=='1' else '1'); await call.message.answer(f'⚠️ Global {key} changed. New multi-channel setup should use channel settings.')
 await call.answer()
@router.message(Command('maintenance'))
async def maintenance(m:Message,db):
 if not await allowed(db,m.from_user.id,'settings'): return
 v=await db.get_setting('maintenance','0'); await db.set_setting('maintenance','0' if v=='1' else '1'); await m.answer('Maintenance '+('🟢 ON' if v!='1' else '🔴 OFF'))
@router.message(Command('ownerusername'))
async def owner(m:Message,db):
 if not await allowed(db,m.from_user.id,'settings'): return
 p=m.text.split(maxsplit=1)
 if len(p)!=2: return await m.answer('Usage: /ownerusername USERNAME')
 await db.set_setting('owner_username',p[1].lstrip('@')); await m.answer('✅ Owner username saved. Restart bot once if dashboard link still shows old username.')
