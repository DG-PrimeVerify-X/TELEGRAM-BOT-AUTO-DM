from aiogram import Router
from aiogram.types import ChatJoinRequest,CallbackQuery
from app.services.admins import allowed
router=Router()
@router.chat_join_request()
async def join(req:ChatJoinRequest,request_service): await request_service.receive_new(req)
@router.callback_query(lambda c:c.data in {'req:new','req:old'})
async def req(c:CallbackQuery,db):
 if not await allowed(db,c.from_user.id,'requests'): return await c.answer('🔒 Access required.',show_alert=True)
 k='new' if c.data=='req:new' else None; n=await db.pending_count(k); await c.message.answer(f'🆕 Requests\n\nPending: <b>{n}</b>'); await c.answer()
