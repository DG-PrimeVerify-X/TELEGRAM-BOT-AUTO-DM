from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.services.admins import allowed, assigned_channels
router=Router()

def picker(chans):
    rows=[[InlineKeyboardButton(text=title,callback_data=f"prediction:channel:{cid}")] for cid,title in chans]
    rows.append([InlineKeyboardButton(text="⬅️ Back",callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def kb(cid,on):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Auto Prediction: {'🟢 ON' if on else '🔴 OFF'}",callback_data=f"prediction:toggle:{cid}")],
        [InlineKeyboardButton(text="📈 Statistics",callback_data=f"prediction:stats:{cid}"),InlineKeyboardButton(text="📜 History",callback_data=f"prediction:history:{cid}")],
        [InlineKeyboardButton(text="⬅️ Channels",callback_data="set:prediction")]
    ])

@router.callback_query(lambda c:c.data.startswith('prediction:'))
async def prediction_callbacks(call,db):
    if not await allowed(db,call.from_user.id,'settings'):
        await call.answer('🔒 Access required. Contact Owner.',show_alert=True); return
    parts=call.data.split(':')
    action=parts[1]
    if action=='channel':
        cid=int(parts[2])
        if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
        ch=await db.get_channel(cid)
        await call.message.answer(f"🤖 <b>1M Auto Prediction</b>\n\n📢 {ch[1]}\nStatus: {'🟢 ON' if ch[7] else '🔴 OFF'}\n\nSource: WinGo 1M live history feed",reply_markup=kb(cid,bool(ch[7])))
    elif action=='toggle':
        cid=int(parts[2])
        if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
        ch=await db.get_channel(cid); cur=int(ch[7]); await db.update_channel(cid,auto_prediction=0 if cur else 1)
        await call.message.answer(f"📢 {ch[1]}\n🤖 1M Auto Prediction: {'🔴 OFF' if cur else '🟢 ON'}")
    elif action=='stats':
        cid=int(parts[2]);
        if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
        ch=await db.get_channel(cid); st=await db.prediction_stats(cid)
        await call.message.answer(f"📊 <b>1M Prediction Stats</b>\n📢 {ch[1]}\n\nTotal: {st['total']}\n✅ WIN: {st['win']}\n❌ LOSS: {st['loss']}\n🎯 JACKPOT: {st['jackpot']}\n⏳ Pending: {st['pending']}")
    elif action=='history':
        cid=int(parts[2]);
        if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
        rows=await db.list_predictions(cid)
        text='📜 <b>1M Prediction History</b>\n\n'
        text+='\n'.join(f"<code>{r[0]}</code> • {r[1]} / {r[2]} • {r[7]}" for r in rows) if rows else 'No prediction history yet.'
        await call.message.answer(text)
    await call.answer()
