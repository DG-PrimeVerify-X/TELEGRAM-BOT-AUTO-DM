from aiogram import Router
from aiogram.filters import Command
from app.services.admins import allowed
from aiogram.types import MessageEntity
router=Router()
@router.callback_query(lambda c:c.data=='premium:page')
async def page(call,db):
    if not await allowed(db,call.from_user.id,'settings'): await call.answer('⛔ Access denied',show_alert=True); return
    cid=await db.get_setting('premium_emoji_id',''); fallback=await db.get_setting('premium_emoji_fallback','✨')
    text=f'{fallback} Premium / Custom Emoji\n\nCustom Emoji ID: {cid or "Not set"}\nFallback: {fallback}\n\nUse /setpremiumemoji CUSTOM_EMOJI_ID.'
    if cid:
        entity=MessageEntity(type='custom_emoji',offset=0,length=len(fallback.encode('utf-16-le'))//2,custom_emoji_id=cid)
        await call.message.answer(text,entities=[entity])
    else: await call.message.answer(text)
    await call.answer()
@router.message(Command('setpremiumemoji'))
async def setemoji(message,db):
    if not await allowed(db,message.from_user.id,'settings'): return
    parts=message.text.split(maxsplit=1)
    if len(parts)!=2 or not parts[1].strip().isdigit(): await message.answer('Usage: /setpremiumemoji CUSTOM_EMOJI_ID'); return
    await db.set_setting('premium_emoji_id',parts[1].strip()); await message.answer('✅ Premium custom emoji ID saved.')
