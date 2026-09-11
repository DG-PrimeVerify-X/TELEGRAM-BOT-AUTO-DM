from aiogram import Router
from aiogram.types import CallbackQuery,Message
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.services.admins import allowed
router=Router()
class BroadcastStates(StatesGroup): waiting_content=State()
@router.callback_query(lambda c:c.data=='broadcast:start')
async def start(call,state,db):
    if not await allowed(db,call.from_user.id,'broadcast'): await call.answer('⛔ Access denied',show_alert=True); return
    await state.set_state(BroadcastStates.waiting_content); await call.message.answer('📢 Send anything to broadcast to <b>All Users</b>. Text, photo, video, audio, document, ZIP, APK etc.\n/cancel to stop.'); await call.answer()
@router.message(BroadcastStates.waiting_content,Command('cancel'))
async def cancel(message,state): await state.clear(); await message.answer('❌ Broadcast cancelled.')
@router.message(BroadcastStates.waiting_content)
async def run(message,state,broadcast_service,db):
    if not await allowed(db,message.from_user.id,'broadcast'): await state.clear(); return
    users=await db.list_users(); await message.answer(f'📤 Broadcasting to <b>{len(users)}</b> users...'); sent,failed=await broadcast_service.copy_message(message.chat.id,message.message_id,users); await db.log(message.from_user.id,'broadcast_completed',f'sent={sent},failed={failed}'); await message.answer(f'📊 <b>Broadcast complete</b>\n\n✅ Sent: {sent}\n⚠️ Failed: {failed}'); await state.clear()
