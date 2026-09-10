from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from app.keyboards.admin import main_menu
from app.services.admins import allowed
router=Router()
@router.message(CommandStart())
async def start(message:Message,db):
    await db.upsert_user(message.from_user.id,message.from_user.username,message.from_user.full_name)
    if not await allowed(db,message.from_user.id,"stats"):
        await message.answer("👋 Welcome! This bot is configured for authorized administrators."); return
    await message.answer("💎 <b>ADMIN CONTROL PANEL</b>",reply_markup=main_menu())
@router.message(Command("panel"))
async def panel(message:Message,db):
    await db.upsert_user(message.from_user.id,message.from_user.username,message.from_user.full_name)
    if await allowed(db,message.from_user.id,"stats"): await message.answer("💎 <b>ADMIN CONTROL PANEL</b>",reply_markup=main_menu())
