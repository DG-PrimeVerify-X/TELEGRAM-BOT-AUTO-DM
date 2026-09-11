from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup,State
from aiogram.types import CallbackQuery,Message
from app.services.admins import allowed,assigned_channels
from app.keyboards.admin import post_targets,post_action
from datetime import datetime
router=Router()
class S(StatesGroup): content=State(); time=State()
@router.callback_query(lambda c:c.data=='post:start')
async def start(c,state,db):
 if not await allowed(db,c.from_user.id,'posts'): return await c.answer('🔒 Access required.',show_alert=True)
 rows=await assigned_channels(db,c.from_user.id); await c.message.answer('📣 Select target channel:',reply_markup=post_targets(rows)); await c.answer()
@router.callback_query(lambda c:c.data.startswith('post:channel:'))
async def channel(c,state,db):
 cid=int(c.data.rsplit(':',1)[1])
 if not await allowed(db,c.from_user.id,'posts') or not await db.has_channel_access(c.from_user.id,cid): return await c.answer('🔒 Channel access required.',show_alert=True)
 await state.update_data(target_type='channel',target_chat_id=cid); await state.set_state(S.content); await c.message.answer('📨 Send content now.'); await c.answer()
@router.callback_query(lambda c:c.data=='post:allusers')
async def allu(c,state,db):
 if not await allowed(db,c.from_user.id,'posts'): return await c.answer('🔒 Access required.',show_alert=True)
 await state.update_data(target_type='all_users',target_chat_id=0); await state.set_state(S.content); await c.message.answer('📨 Send content now.'); await c.answer()
@router.message(S.content,Command('cancel'))
async def cancel(m,state): await state.clear(); await m.answer('❌ Cancelled')
@router.message(S.content)
async def content(m,state): await state.update_data(source_chat_id=m.chat.id,source_message_id=m.message_id); await m.answer('Content received.',reply_markup=post_action())
@router.callback_query(lambda c:c.data in {'post:sendnow','post:schedule'})
async def action(c,state,db,post_service):
 d=await state.get_data()
 if c.data=='post:sendnow':
  try:
   if d['target_type']=='all_users': s,f=await post_service.copy_to_all_users(d['source_chat_id'],d['source_message_id']); await c.message.answer(f'✅ Sent {s}, failed {f}')
   else: await post_service.copy_saved(d['source_chat_id'],d['source_message_id'],d['target_chat_id']); await c.message.answer('✅ Post sent.')
  except Exception as e: await c.message.answer(f'❌ {type(e).__name__}')
  await state.clear(); return await c.answer()
 await state.set_state(S.time); await c.message.answer('⏰ Time: YYYY-MM-DD HH:MM (IST)'); await c.answer()
@router.message(S.time,Command('cancel'))
async def ct(m,state): await state.clear(); await m.answer('❌ Cancelled')
@router.message(S.time)
async def schedule(m,state,db):
 d=await state.get_data()
 try: run=datetime.strptime(m.text.strip(),'%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')
 except: return await m.answer('⚠️ Wrong format')
 sid=await db.save_schedule(d['source_chat_id'],d['source_message_id'],d['target_type'],d['target_chat_id'],run,m.from_user.id); await state.clear(); await m.answer(f'⏰ Scheduled ID <code>{sid}</code>')
@router.callback_query(lambda c:c.data=='post:schedules')
async def sched(c,db):
 if not await allowed(db,c.from_user.id,'schedules'): return await c.answer('🔒 Access required.',show_alert=True)
 rows=await db.list_schedules(); await c.message.answer('⏰ Schedules\n\n'+('\n'.join(f'{r[0]} • {r[1]} • {r[2]} • {r[3]}' for r in rows) or 'None')); await c.answer()
@router.callback_query(lambda c:c.data=='post:cancel')
async def cancel_cb(c,state): await state.clear(); await c.answer('Cancelled')
