import asyncio
class BroadcastService:
 def __init__(self,bot,db): self.bot,self.db=bot,db
 async def copy_message(self,src,mid,users):
  s=f=0
  for uid in users:
   try: await self.bot.copy_message(chat_id=uid,from_chat_id=src,message_id=mid); s+=1
   except Exception: f+=1
   await asyncio.sleep(.06)
  return s,f
