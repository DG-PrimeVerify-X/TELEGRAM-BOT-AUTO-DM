import asyncio
from aiogram.types import ReactionTypeEmoji,ReactionTypeCustomEmoji
class PostService:
 def __init__(self,bot,db): self.bot,self.db=bot,db
 async def react(self,cid,mid):
  row=await self.db.channel(cid)
  if not row or not row[9]: return
  custom=row[10] or ''; emoji=row[9] or '👍'
  try: await self.bot.set_message_reaction(chat_id=cid,message_id=mid,reaction=[ReactionTypeCustomEmoji(custom_emoji_id=custom)] if custom else [ReactionTypeEmoji(emoji=emoji)])
  except Exception: pass
 async def copy_saved(self,src,mid,target):
  m=await self.bot.copy_message(chat_id=target,from_chat_id=src,message_id=mid); await self.react(target,m.message_id); return m
 async def copy_to_all_users(self,src,mid):
  s=f=0
  for uid in await self.db.list_users():
   try: await self.bot.copy_message(chat_id=uid,from_chat_id=src,message_id=mid); s+=1
   except Exception: f+=1
   await asyncio.sleep(.06)
  return s,f
