from aiogram import Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,CallbackQuery
from app.keyboards.admin import main_menu,access_keyboard
from app.services.admins import allowed
router=Router()

async def owner(db,config):
    return (await db.get_setting("owner_username","")) or config.owner_username

@router.message(CommandStart())
async def start(message:Message,db,config):
    await db.upsert_user(message.from_user.id,message.from_user.username,message.from_user.full_name)
    o=await owner(db,config)
    await message.answer("💎 <b>ADMIN CONTROL PANEL</b>\n\n🔐 Admin functions require Owner access approval.",
                         reply_markup=main_menu(o))

@router.message(Command("panel"))
async def panel(message:Message,db,config):
    await db.upsert_user(message.from_user.id,message.from_user.username,message.from_user.full_name)
    o=await owner(db,config)
    await message.answer("💎 <b>ADMIN CONTROL PANEL</b>",reply_markup=main_menu(o))

async def deny(call:CallbackQuery,db,config,permission="stats"):
    if await allowed(db,call.from_user.id,permission): return False
    o=await owner(db,config)
    await call.answer("🔒 Access required. Contact Owner.",show_alert=True)
    try: await call.message.answer("🔐 <b>Access Required</b>\n\nOwner se access lene ke baad admin functions use kar sakte ho.",reply_markup=access_keyboard(o))
    except Exception: pass
    return True
