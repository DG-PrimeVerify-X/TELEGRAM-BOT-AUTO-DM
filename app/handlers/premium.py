from aiogram import Router
from aiogram.filters import Command
from aiogram.types import MessageEntity
from app.services.admins import allowed
router=Router()
@router.callback_query(lambda c:c.data=='premium:page')
async def page(c,db):
 if not await allowed(db,c.from_user.id,'settings'): return await c.answer('🔒 Access required.',show_alert=True)
 cid=await db.get_setting('premium_emoji_id',''); await c.message.answer(f'💎 Premium Emoji\n\nID: {cid or "Not set"}\n/setpremiumemoji CUSTOM_EMOJI_ID'); await c.answer()
@router.message(Command('setpremiumemoji'))
async def setemoji(m,db):
 if not await allowed(db,m.from_user.id,'settings'): return
 p=m.text.split(maxsplit=1)
 if len(p)!=2 or not p[1].isdigit(): return await m.answer('Usage: /setpremiumemoji ID')
 await db.set_setting('premium_emoji_id',p[1]); await m.answer('✅ Premium emoji saved.')
