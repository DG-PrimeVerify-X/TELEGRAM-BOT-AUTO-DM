import asyncio
from aiogram import Bot
from aiogram.types import Message, ReactionTypeEmoji, ReactionTypeCustomEmoji

class PostService:
    def __init__(self,bot,db): self.bot,self.db=bot,db
    async def react(self,chat_id,message_id):
        if await self.db.get_setting("auto_reaction","0")!="1": return
        custom=await self.db.get_setting("reaction_custom_emoji_id","")
        emoji=await self.db.get_setting("reaction_emoji","👍")
        try:
            reaction=[ReactionTypeCustomEmoji(custom_emoji_id=custom)] if custom else [ReactionTypeEmoji(emoji=emoji)]
            await self.bot.set_message_reaction(chat_id=chat_id,message_id=message_id,reaction=reaction)
        except Exception: pass
    async def copy_saved(self,source_chat_id,source_message_id,target_chat_id):
        sent=await self.bot.copy_message(chat_id=target_chat_id,from_chat_id=source_chat_id,message_id=source_message_id)
        await self.react(target_chat_id,sent.message_id); return sent
    async def copy_to(self,message,target_chat_id): return await self.copy_saved(message.chat.id,message.message_id,target_chat_id)
    async def copy_to_all_users(self,source_chat_id,source_message_id):
        sent=failed=0
        for uid in await self.db.list_users():
            try: await self.bot.copy_message(chat_id=uid,from_chat_id=source_chat_id,message_id=source_message_id); sent+=1
            except Exception: failed+=1
            await asyncio.sleep(.08)
        return sent,failed
