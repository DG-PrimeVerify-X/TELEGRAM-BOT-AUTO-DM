from aiogram import Router
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
from app.services.admins import allowed,is_super_admin
from app.keyboards.admin import access_keyboard
router=Router()

class AddChannel(StatesGroup):
    waiting_forward=State()

@router.callback_query(lambda c:c.data=="channels:list")
async def list_channels(call,db,config):
    if not await allowed(db,call.from_user.id,"channels"):
        await call.answer("🔒 Access required. Contact Owner.",show_alert=True); return
    rows=await db.list_channels()
    text="📢 <b>Channel Manager</b>\n\n"+("\n".join(f"• {r[1]} — <code>{r[0]}</code>\n  AA:{r[3]} DM:{r[4]} Post:{r[5]} React:{r[6]} Pred:{r[7]}" for r in rows) if rows else "No channels added.")
    text+="\n\n➕ Use /addchannel and forward any post from the channel."
    await call.message.answer(text); await call.answer()

@router.message(lambda m:m.text and m.text.strip()=="/addchannel")
async def add_start(message,state,db):
    if not await allowed(db,message.from_user.id,"channels"): return
    await state.set_state(AddChannel.waiting_forward)
    await message.answer("➕ <b>Add Channel</b>\n\nChannel ka koi bhi post yahan <b>forward</b> karo.\nBot admin hona zaroori hai.\n/cancel to stop.")

@router.message(AddChannel.waiting_forward)
async def add_forward(message,state,db,bot):
    if message.text=="/cancel":
        await state.clear(); await message.answer("❌ Cancelled."); return
    origin=getattr(message,"forward_origin",None)
    chat=getattr(origin,"chat",None) if origin else None
    if not chat:
        await message.answer("⚠️ Channel post forward karo.")
        return
    try:
        me=await bot.get_me()
        member=await bot.get_chat_member(chat.id,me.id)
        if getattr(member,"status","") not in ("administrator","creator"):
            await message.answer("❌ Bot is channel admin nahi hai.")
            return
        if not getattr(member,"can_post_messages",True):
            await message.answer("⚠️ Bot ko Post Messages permission do.")
            return
        if getattr(chat,"type","") == "channel" and not getattr(member,"can_invite_users",True):
            await message.answer("⚠️ Bot ko Invite Users / Approve Join Requests permission do.")
            return
        await db.add_channel(chat.id,chat.title or str(chat.id),getattr(chat,"username",None) or "")
        await state.clear()
        await message.answer(f"✅ Channel Added\n\n<b>{chat.title}</b>\n<code>{chat.id}</code>\n\nAb Super Admin admin assign karke per-channel automation ON kar sakta hai.")
    except Exception as e:
        await message.answer(f"⚠️ Channel check failed: <code>{type(e).__name__}</code>")
