from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message,CallbackQuery
from app.keyboards.admin import main_menu,access
from app.services.admins import allowed
router=Router()
async def dashboard(message,db,config): await message.answer('💎 <b>ADMIN CONTROL PANEL</b>\n\n🔐 Unauthorized users can view the dashboard, but actions require Owner access.',reply_markup=main_menu(config.owner_username))
@router.message(CommandStart())
async def start(message:Message,db,config): await db.upsert_user(message.from_user.id,message.from_user.username,message.from_user.full_name); await dashboard(message,db,config)
@router.callback_query(lambda c:c.data=='access:denied')
async def denied(call:CallbackQuery,config): await call.answer('🔒 Access required. Contact Owner.',show_alert=True); await call.message.answer('🔒 <b>Access Required</b>\nContact the Owner to get admin access.',reply_markup=access(config.owner_username))
