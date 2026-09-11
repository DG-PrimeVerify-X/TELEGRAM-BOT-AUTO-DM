from aiogram import Router
from aiogram.types import CallbackQuery,Message
from app.services.admins import allowed,assigned_channels
router=Router()
@router.channel_post()
async def post(m:Message,post_service): await post_service.react(m.chat.id,m.message_id)
@router.callback_query(lambda c:c.data=='reaction:page')
async def page(c,db):
 if not await allowed(db,c.from_user.id,'reaction'): return await c.answer('🔒 Access required.',show_alert=True)
 rows=await assigned_channels(db,c.from_user.id); await c.message.answer('❤️ Auto Reaction is channel-wise. Use /channelsettings CHANNEL_ID.\n\n'+('\n'.join(f'{r[1]} — ID {r[0]}' for r in rows) or 'No assigned channels.')); await c.answer()
