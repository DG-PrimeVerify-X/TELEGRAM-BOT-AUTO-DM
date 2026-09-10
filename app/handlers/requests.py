from aiogram import Router
from aiogram.types import ChatJoinRequest, CallbackQuery
from app.services.admins import allowed
router = Router()
@router.chat_join_request()
async def join_request(req: ChatJoinRequest, request_service): await request_service.receive_new(req)
@router.callback_query(lambda c: c.data in {"req:new","req:old"})
async def request_stats(call: CallbackQuery, db):
    if not await allowed(db, call.from_user.id, "requests"): await call.answer("⛔ Access denied", show_alert=True); return
    kind='new' if call.data=='req:new' else 'old'; count=await db.pending_count(kind); label='New' if kind=='new' else 'Old/Pending'; await call.message.answer(f"{'🆕' if kind=='new' else '🕐'} <b>{label} Requests</b>\n\nPending: <b>{count}</b>"); await call.answer()
