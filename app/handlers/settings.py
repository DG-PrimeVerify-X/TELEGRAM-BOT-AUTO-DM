from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.admin import main_menu
from app.services.admins import allowed
router = Router()

def toggle_keyboard(key, value):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{key}: {'🟢 ON' if value=='1' else '🔴 OFF'}", callback_data=f"toggle:{key}")],[InlineKeyboardButton(text="⬅️ Back", callback_data="back")]])

@router.callback_query(lambda c: c.data.startswith("toggle:"))
async def toggle(call: CallbackQuery, db):
    if not await allowed(db, call.from_user.id, "settings"):
        await call.answer("⛔ Access denied", show_alert=True); return
    key = call.data.split(":", 1)[1]; cur = await db.get_setting(key, "0"); await db.set_setting(key, "0" if cur == '1' else '1')
    await call.message.answer(f"⚙️ {key.replace('_',' ').title()}: {'🟢 ON' if cur != '1' else '🔴 OFF'}"); await call.answer()

@router.callback_query(lambda c: c.data in {"set:dm", "set:accept", "settings"})
async def page(call: CallbackQuery, db):
    if not await allowed(db, call.from_user.id, "settings"):
        await call.answer("⛔ Access denied", show_alert=True); return
    if call.data == "settings":
        dm = await db.get_setting("auto_dm", "0"); ac = await db.get_setting("auto_accept", "0"); ar = await db.get_setting("auto_reaction", "0")
        await call.message.answer(f"⚙️ <b>Settings</b>\n\n🤖 Auto-DM: {'🟢 ON' if dm=='1' else '🔴 OFF'}\n⚡ Auto Accept: {'🟢 ON' if ac=='1' else '🔴 OFF'}\n❤️ Auto Reaction: {'🟢 ON' if ar=='1' else '🔴 OFF'}")
    else:
        key = 'auto_dm' if call.data == 'set:dm' else 'auto_accept'; v = await db.get_setting(key, '0')
        await call.message.answer(f"⚙️ <b>{key.replace('_',' ').title()}</b>", reply_markup=toggle_keyboard(key, v))
    await call.answer()

@router.callback_query(lambda c: c.data == "back")
async def back(call: CallbackQuery):
    await call.message.answer("💎 <b>ADMIN CONTROL PANEL</b>", reply_markup=main_menu()); await call.answer()
