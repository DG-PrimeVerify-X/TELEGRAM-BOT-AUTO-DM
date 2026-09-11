from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from app.services.admins import allowed, assigned_channels
router=Router()

def picker(chans):
    rows=[[InlineKeyboardButton(text=title,callback_data=f"reaction:channel:{cid}")] for cid,title in chans]
    rows.append([InlineKeyboardButton(text="⬅️ Back",callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def keyboard(cid,on,emoji):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Auto Reaction: {'🟢 ON' if on else '🔴 OFF'}",callback_data=f"reaction:toggle:{cid}")],
        [InlineKeyboardButton(text="👍 Set 👍",callback_data=f"reaction:set:{cid}:👍"),InlineKeyboardButton(text="❤️ Set ❤️",callback_data=f"reaction:set:{cid}:❤️")],
        [InlineKeyboardButton(text="🔥 Set 🔥",callback_data=f"reaction:set:{cid}:🔥"),InlineKeyboardButton(text="🎉 Set 🎉",callback_data=f"reaction:set:{cid}:🎉")],
        [InlineKeyboardButton(text="⬅️ Channels",callback_data="reaction:page")]
    ])

@router.channel_post()
async def every_channel_post(message:Message,db,post_service):
    await post_service.react(message.chat.id,message.message_id)

@router.callback_query(lambda c:c.data=='reaction:page')
async def page(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    chans=await assigned_channels(db,call.from_user.id)
    if not chans: await call.message.answer('⚠️ No channel assigned.'); await call.answer(); return
    await call.message.answer('❤️ <b>Select channel for Auto Reaction</b>',reply_markup=picker(chans)); await call.answer()

@router.callback_query(lambda c:c.data.startswith('reaction:channel:'))
async def channel_page(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    cid=int(call.data.rsplit(':',1)[1])
    if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
    ch=await db.get_channel(cid)
    if not ch: await call.answer('⚠️ Channel not found',show_alert=True); return
    await call.message.answer(f"❤️ <b>Auto Reaction</b>\n\n📢 {ch[1]}\nStatus: {'🟢 ON' if ch[7] else '🔴 OFF'}\nReaction: {ch[9] or ch[8] or '👍'}",reply_markup=keyboard(cid,bool(ch[7]),ch[8])); await call.answer()

@router.callback_query(lambda c:c.data.startswith('reaction:toggle:'))
async def toggle(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    cid=int(call.data.rsplit(':',1)[1])
    if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
    ch=await db.get_channel(cid); cur=int(ch[7]); await db.update_channel(cid,auto_reaction=0 if cur else 1)
    await call.message.answer(f"📢 {ch[1]}\n❤️ Auto Reaction: {'🔴 OFF' if cur else '🟢 ON'}"); await call.answer()

@router.callback_query(lambda c:c.data.startswith('reaction:set:'))
async def set_emoji(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    _,_,cid_s,emoji=call.data.split(':',3); cid=int(cid_s)
    if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
    await db.update_channel(cid,reaction_custom_emoji_id='',reaction_emoji=emoji,auto_reaction=1)
    await call.message.answer(f'✅ Reaction set to {emoji} and enabled for this channel.'); await call.answer()
