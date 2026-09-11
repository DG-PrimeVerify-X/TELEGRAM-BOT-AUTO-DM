from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup,State
from app.services.admins import allowed
router=Router()
class S(StatesGroup): content=State()
@router.callback_query(lambda c:c.data=='broadcast:start')
async def start(c,state,db):
 if not await allowed(db,c.from_user.id,'broadcast'): return await c.answer('🔒 Access required.',show_alert=True)
 await state.set_state(S.content); await c.message.answer('📢 Send message/media to broadcast. /cancel'); await c.answer()
@router.message(S.content,Command('cancel'))
async def cancel(m,state): await state.clear(); await m.answer('❌ Cancelled')
@router.message(S.content)
async def send(m,state,db,broadcast_service):
 if not await allowed(db,m.from_user.id,'broadcast'): await state.clear(); return
 users=await db.list_users(); await m.answer(f'📤 Sending to {len(users)} users...'); sent,failed=await broadcast_service.copy_message(m.chat.id,m.message_id,users); await db.log(m.from_user.id,'broadcast',f'{sent}/{failed}'); await m.answer(f'📊 Done\n✅ {sent}\n⚠️ {failed}'); await state.clear()
