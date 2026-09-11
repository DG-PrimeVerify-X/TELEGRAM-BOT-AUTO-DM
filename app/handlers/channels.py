from aiogram import Router
from aiogram.types import Message,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.filters import Command
from app.services.admins import allowed,superadmin
router=Router()
def kb(cid,row):
 return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f'⚡ Auto Accept: {"ON" if row[5] else "OFF"}',callback_data=f'ch:toggle:{cid}:auto_accept'),InlineKeyboardButton(text=f'🤖 Auto DM: {"ON" if row[6] else "OFF"}',callback_data=f'ch:toggle:{cid}:auto_dm')],[InlineKeyboardButton(text=f'📣 Auto Post: {"ON" if row[7] else "OFF"}',callback_data=f'ch:toggle:{cid}:auto_post'),InlineKeyboardButton(text=f'❤️ Reaction: {"ON" if row[8] else "OFF"}',callback_data=f'ch:toggle:{cid}:auto_reaction')],[InlineKeyboardButton(text='👍 Set 👍',callback_data=f'ch:react:{cid}:👍'),InlineKeyboardButton(text='❤️ Set ❤️',callback_data=f'ch:react:{cid}:❤️'),InlineKeyboardButton(text='🔥 Set 🔥',callback_data=f'ch:react:{cid}:🔥')]])
@router.callback_query(lambda c:c.data=='channels:page')
async def page(c:CallbackQuery,db):
 if not await allowed(db,c.from_user.id,'channels'): return await c.answer('🔒 Access required.',show_alert=True)
 rows=await db.list_channels(); text='📢 <b>Channel Manager</b>\n\n' + ('\n'.join(f'• <code>{x[0]}</code> — {x[1]}' for x in rows) if rows else 'No channels added.') + '\n\n/addchannel CHANNEL_ID\n/assignchannel ADMIN_ID CHANNEL_ID'
 await c.message.answer(text); await c.answer()
@router.message(Command('addchannel'))
async def add(m:Message,db,bot):
 if not await allowed(db,m.from_user.id,'channels'): return
 p=m.text.split(); cid=int(p[1]) if len(p)==2 and p[1].lstrip('-').isdigit() else None
 if cid is None and m.reply_to_message:
  o=getattr(m.reply_to_message,'forward_origin',None); chat=getattr(o,'chat',None); cid=getattr(chat,'id',None)
 if not cid: return await m.answer('Usage: /addchannel CHANNEL_ID\nOr reply to a forwarded channel post with /addchannel')
 try:
  chat=await bot.get_chat(cid); me=await bot.get_me(); member=await bot.get_chat_member(cid,me.id)
  if member.status not in ('administrator','creator'): return await m.answer('❌ Bot is not admin in this channel.')
  if hasattr(member,'can_invite_users') and member.can_invite_users is False: return await m.answer('⚠️ Bot admin found, but join-request permission may be missing.')
  await db.add_channel(cid,chat.title or str(cid),getattr(chat,'username','') or '')
  await m.answer(f'✅ Channel added & bot admin verified.\n<b>{chat.title}</b>\n<code>{cid}</code>\n\nNow assign an admin and configure channel automation.')
 except Exception as e: await m.answer(f'❌ Channel setup failed: <code>{type(e).__name__}</code>')
@router.message(Command('removechannel'))
async def remove(m:Message,db):
 if not await allowed(db,m.from_user.id,'channels'): return
 p=m.text.split();
 if len(p)!=2 or not p[1].lstrip('-').isdigit(): return await m.answer('Usage: /removechannel CHANNEL_ID')
 await db.remove_channel(int(p[1])); await m.answer('🗑️ Channel removed.')
@router.message(Command('assignchannel'))
async def assign(m:Message,db):
 if not await allowed(db,m.from_user.id,'channels'): return
 p=m.text.split();
 if len(p)!=3 or not p[1].isdigit() or not p[2].lstrip('-').isdigit(): return await m.answer('Usage: /assignchannel ADMIN_ID CHANNEL_ID')
 if not await db.channel(int(p[2])): return await m.answer('❌ Channel not registered.')
 if not await db.permissions(int(p[1])): return await m.answer('❌ Admin not registered. Add admin first.')
 await db.assign_channel(int(p[1]),int(p[2])); await m.answer('✅ Channel assigned to admin.')
@router.message(Command('channelsettings'))
async def channelsettings(m:Message,db):
 if not await allowed(db,m.from_user.id,'channels'): return
 p=m.text.split();
 if len(p)!=2 or not p[1].lstrip('-').isdigit(): return await m.answer('Usage: /channelsettings CHANNEL_ID')
 cid=int(p[1]); row=await db.channel(cid)
 if not row or not await db.has_channel_access(m.from_user.id,cid): return await m.answer('❌ No channel access.')
 await m.answer(f'📢 <b>{row[2]}</b>\nID: <code>{cid}</code>',reply_markup=kb(cid,row))
@router.callback_query(lambda c:c.data.startswith('ch:toggle:'))
async def toggle(c:CallbackQuery,db):
 _,_,cid,key=c.data.split(':'); cid=int(cid)
 if not await allowed(db,c.from_user.id,'channels') or not await db.has_channel_access(c.from_user.id,cid): return await c.answer('🔒 Channel access required.',show_alert=True)
 row=await db.channel(cid); old=row[5+['auto_accept','auto_dm','auto_post','auto_reaction'].index(key)]; await db.set_channel(cid,key,0 if old else 1); row=await db.channel(cid); await c.message.edit_reply_markup(reply_markup=kb(cid,row)); await c.answer('Updated')
@router.callback_query(lambda c:c.data.startswith('ch:react:'))
async def react(c:CallbackQuery,db):
 _,_,cid,emoji=c.data.split(':'); cid=int(cid)
 if not await allowed(db,c.from_user.id,'channels') or not await db.has_channel_access(c.from_user.id,cid): return await c.answer('🔒 Channel access required.',show_alert=True)
 await db.set_channel(cid,'reaction_emoji',emoji); await db.set_channel(cid,'reaction_custom_emoji_id',''); await db.set_channel(cid,'auto_reaction',1); await c.answer(f'Reaction {emoji} enabled')
