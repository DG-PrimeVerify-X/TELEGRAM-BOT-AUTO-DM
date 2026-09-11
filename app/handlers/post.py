from datetime import datetime
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.keyboards.admin import channels_keyboard, post_action_keyboard
from app.services.admins import allowed, assigned_channels
router = Router()
class PostStates(StatesGroup):
    waiting_content = State(); waiting_time = State()
@router.callback_query(lambda c: c.data == 'post:start')
async def start_post(call: CallbackQuery, state: FSMContext, db, config):
    if not await allowed(db, call.from_user.id, 'posts'): await call.answer('⛔ Access denied', show_alert=True); return
    chans = await assigned_channels(db, call.from_user.id)
    if not chans: await call.message.answer('⚠️ No channel assigned. Contact Super Admin.'); await call.answer(); return
    await state.update_data(channels=chans); await call.message.answer('📌 <b>Select target:</b>', reply_markup=channels_keyboard(chans)); await call.answer()
@router.callback_query(lambda c: c.data.startswith('post:channel:'))
async def choose_channel(call, state, db):
    if not await allowed(db, call.from_user.id, 'posts'): await call.answer('⛔ Access denied', show_alert=True); return
    cid=int(call.data.rsplit(':',1)[1]);
    if not await db.is_assigned(call.from_user.id,cid): await call.answer('⛔ Channel access denied',show_alert=True); return
    await state.update_data(target_type='channel',target_chat_id=cid); await state.set_state(PostStates.waiting_content); await call.message.answer('📣 Send the content now. Text, photo, video, audio, document, ZIP, APK etc.\n\n/cancel to stop.'); await call.answer()
@router.callback_query(lambda c: c.data == 'post:allusers')
async def choose_all(call,state,db):
    if not await allowed(db,call.from_user.id,'posts'): await call.answer('⛔ Access denied',show_alert=True); return
    await state.update_data(target_type='all_users',target_chat_id=0); await state.set_state(PostStates.waiting_content); await call.message.answer('👥 <b>All Users selected.</b> Send the content now.\n\n/cancel to stop.'); await call.answer()
@router.callback_query(lambda c: c.data == 'post:cancel')
async def cancel_cb(call,state): await state.clear(); await call.message.answer('❌ Cancelled.'); await call.answer()
@router.message(PostStates.waiting_content, Command('cancel'))
async def cancel(message,state): await state.clear(); await message.answer('❌ Cancelled.')
@router.message(PostStates.waiting_content)
async def receive(message,state): await state.update_data(source_chat_id=message.chat.id,source_message_id=message.message_id); await message.answer('📌 Content received. Choose:',reply_markup=post_action_keyboard())
@router.callback_query(lambda c:c.data in {'post:sendnow','post:schedule'})
async def action(call,state,db,post_service):
    data=await state.get_data()
    if not data.get('target_type') or not data.get('source_message_id'): await call.answer('⚠️ Content missing',show_alert=True); return
    if call.data=='post:sendnow':
        try:
            if data['target_type']=='all_users':
                sent,failed=await post_service.copy_to_all_users(data['source_chat_id'],data['source_message_id']); await call.message.answer(f'✅ Sent to users.\n\n📤 Sent: {sent}\n⚠️ Failed: {failed}')
            else:
                sent=await post_service.copy_saved(data['source_chat_id'],data['source_message_id'],data['target_chat_id']); await db.log(call.from_user.id,'post_sent',str(sent.message_id)); await call.message.answer('✅ Post sent successfully.')
        except Exception as e: await call.message.answer(f'⚠️ Could not send: <code>{type(e).__name__}</code>')
        await state.clear(); await call.answer(); return
    await state.set_state(PostStates.waiting_time); await call.message.answer('⏰ Send date/time in IST format:\n<code>2026-09-11 18:30</code>'); await call.answer()
@router.message(PostStates.waiting_time, Command('cancel'))
async def cancel_time(message,state): await state.clear(); await message.answer('❌ Cancelled.')
@router.message(PostStates.waiting_time)
async def schedule(message,state,db):
    data=await state.get_data()
    try: run_at=datetime.strptime(message.text.strip(),'%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')
    except Exception: await message.answer('⚠️ Wrong format. Use <code>YYYY-MM-DD HH:MM</code>'); return
    sid=await db.save_schedule(data['source_chat_id'],data['source_message_id'],data['target_type'],data['target_chat_id'],run_at,message.from_user.id); await db.log(message.from_user.id,'post_scheduled',f'{sid}:{run_at}'); await state.clear(); await message.answer(f'⏰ <b>Scheduled</b> ID: <code>{sid}</code>\nTime: <code>{run_at}</code>')
@router.callback_query(lambda c:c.data=='post:schedules')
async def schedules(call,db):
    if not await allowed(db,call.from_user.id,'schedules'): await call.answer('⛔ Access denied',show_alert=True); return
    rows=await db.list_schedules(); text='⏰ <b>Scheduled Posts</b>\n\n'+('\n'.join(f'ID <code>{r[0]}</code> • {r[1]} • {r[2]} • {r[3]}' for r in rows) if rows else 'No schedules.'); await call.message.answer(text+'\n\nCancel: <code>/cancelschedule ID</code>'); await call.answer()
@router.message(Command('cancelschedule'))
async def cancel_schedule(message,db):
    if not await allowed(db,message.from_user.id,'schedules'): return
    parts=message.text.split()
    if len(parts)!=2 or not parts[1].isdigit(): await message.answer('Usage: /cancelschedule ID'); return
    n=await db.cancel_schedule(int(parts[1])); await message.answer('✅ Schedule cancelled.' if n else '⚠️ Not found/already completed.')
