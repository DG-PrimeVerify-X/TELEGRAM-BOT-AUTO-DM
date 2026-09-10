from aiogram import Router
from aiogram.types import Message
from app.keyboards.admin import reaction_keyboard
from app.services.admins import allowed
router=Router()
@router.channel_post()
async def every_channel_post(message:Message,db,post_service):
    if await db.get_setting('auto_reaction','0')=='1': await post_service.react(message.chat.id,message.message_id)
@router.callback_query(lambda c:c.data=='reaction:page')
async def page(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    on=await db.get_setting('auto_reaction','0'); emoji=await db.get_setting('reaction_emoji','👍'); custom=await db.get_setting('reaction_custom_emoji_id','')
    await call.message.answer(f'❤️ <b>Auto Reaction</b>\n\nStatus: {"🟢 ON" if on=="1" else "🔴 OFF"}\nReaction: {custom or emoji}\n\nWhen ON, the bot reacts to every new channel post received by the bot.',reply_markup=reaction_keyboard(on=='1')); await call.answer()
@router.callback_query(lambda c:c.data=='reaction:toggle')
async def toggle(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    v=await db.get_setting('auto_reaction','0'); await db.set_setting('auto_reaction','0' if v=='1' else '1'); await call.message.answer('❤️ Auto Reaction: '+('🟢 ON' if v!='1' else '🔴 OFF')); await call.answer()
@router.callback_query(lambda c:c.data.startswith('reaction:set:'))
async def set_emoji(call,db):
    if not await allowed(db,call.from_user.id,'reaction'): await call.answer('⛔ Access denied',show_alert=True); return
    emoji=call.data.rsplit(':',1)[1]; await db.set_setting('reaction_custom_emoji_id',''); await db.set_setting('reaction_emoji',emoji); await db.set_setting('auto_reaction','1'); await call.message.answer(f'✅ Reaction set to {emoji} and Auto Reaction enabled.'); await call.answer()
