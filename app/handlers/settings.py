from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.admin import main_menu
from app.services.admins import allowed, assigned_channels
router = Router()

def channel_picker(chans, feature):
    rows=[[InlineKeyboardButton(text=f"{title}",callback_data=f"chset:{feature}:{cid}")] for cid,title in chans]
    rows.append([InlineKeyboardButton(text="⬅️ Back",callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def toggle_keyboard(feature,cid,value):
    label=feature.replace("_"," ").title()
    return InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text=f"{label}: {'🟢 ON' if value else '🔴 OFF'}",callback_data=f"chtoggle:{feature}:{cid}")],
      [InlineKeyboardButton(text="⬅️ Back",callback_data=f"chset:{feature}:{cid}")]
    ])

@router.callback_query(lambda c:c.data in {"set:dm","set:accept","set:prediction","set:post"})
async def feature_page(call,db):
    if not await allowed(db,call.from_user.id,"settings"):
        await call.answer("🔒 Access required. Contact Owner.",show_alert=True); return
    feature={"set:dm":"auto_dm","set:accept":"auto_accept","set:prediction":"auto_prediction","set:post":"auto_post"}[call.data]
    chans=await assigned_channels(db,call.from_user.id)
    if not chans: await call.message.answer("⚠️ No channel assigned."); await call.answer(); return
    await call.message.answer(f"📢 Select channel for {feature.replace('_',' ').title()}:",reply_markup=channel_picker(chans,feature)); await call.answer()

@router.callback_query(lambda c:c.data.startswith("chset:"))
async def channel_setting_page(call,db):
    if not await allowed(db,call.from_user.id,"settings"):
        await call.answer("🔒 Access required. Contact Owner.",show_alert=True); return
    _,feature,cid_s=call.data.split(":"); cid=int(cid_s)
    if not await db.is_assigned(call.from_user.id,cid): await call.answer("⛔ Channel access denied",show_alert=True); return
    ch=await db.get_channel(cid)
    if not ch: await call.answer("⚠️ Channel not found",show_alert=True); return
    idx={"auto_dm":4,"auto_accept":3,"auto_prediction":7,"auto_post":5}[feature]
    await call.message.answer(f"⚙️ <b>{feature.replace('_',' ').title()}</b>\n\n📢 {ch[1]}",reply_markup=toggle_keyboard(feature,cid,bool(ch[idx])))
    await call.answer()

@router.callback_query(lambda c:c.data.startswith("chtoggle:"))
async def channel_toggle(call,db):
    if not await allowed(db,call.from_user.id,"settings"):
        await call.answer("🔒 Access required. Contact Owner.",show_alert=True); return
    _,feature,cid_s=call.data.split(":"); cid=int(cid_s)
    if not await db.is_assigned(call.from_user.id,cid): await call.answer("⛔ Channel access denied",show_alert=True); return
    ch=await db.get_channel(cid)
    if not ch: await call.answer("⚠️ Channel not found",show_alert=True); return
    idx={"auto_dm":4,"auto_accept":3,"auto_prediction":7,"auto_post":5}[feature]; cur=int(ch[idx]); await db.update_channel(cid,**{feature:0 if cur else 1})
    await call.message.answer(f"✅ {feature.replace('_',' ').title()}: {'🟢 ON' if not cur else '🔴 OFF'}\n📢 {ch[1]}")
    await call.answer()

@router.callback_query(lambda c:c.data=="settings")
async def settings_page(call,db):
    if not await allowed(db,call.from_user.id,"settings"):
        await call.answer("🔒 Access required. Contact Owner.",show_alert=True); return
    chans=await assigned_channels(db,call.from_user.id)
    if not chans: await call.message.answer("⚙️ Settings\n\nNo channels assigned."); await call.answer(); return
    lines=[]
    for cid,title in chans:
        ch=await db.get_channel(cid)
        lines.append(f"📢 <b>{title}</b> — Accept {'🟢' if ch[3] else '🔴'} | DM {'🟢' if ch[4] else '🔴'} | Post {'🟢' if ch[5] else '🔴'} | React {'🟢' if ch[6] else '🔴'} | Pred {'🟢' if ch[7] else '🔴'}")
    await call.message.answer("⚙️ <b>Channel Settings</b>\n\n"+"\n".join(lines)+"\n\nUse Auto-DM / Auto Accept buttons to change a channel.")
    await call.answer()

@router.callback_query(lambda c:c.data=="back")
async def back(call,db,config):
    o=(await db.get_setting("owner_username","")) or config.owner_username
    await call.message.answer("💎 <b>ADMIN CONTROL PANEL</b>",reply_markup=main_menu(o)); await call.answer()
