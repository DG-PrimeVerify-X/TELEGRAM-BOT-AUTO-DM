from aiogram.types import MessageEntity
class RequestService:
 def __init__(self,bot,db): self.bot,self.db=bot,db
 async def receive_new(self,req):
  u=req.from_user; cid=req.chat.id; await self.db.add_request(u.id,cid,u.username,u.full_name,'new'); row=await self.db.channel(cid)
  if not row: return 'unregistered'
  if await self.db.get_setting('maintenance','0')=='1': return 'maintenance'
  accepted=False
  if row[6]:
   try: await self.bot.approve_chat_join_request(cid,u.id); accepted=True
   except Exception: return 'accept_failed'
  if accepted and row[7]:
   name=u.full_name or 'there'; text=(row[12] or '✨ Welcome {name}! Your request has been accepted.').replace('{name}',name).replace('{username}',u.username or '')
   try:
    eid=await self.db.get_setting('premium_emoji_id',''); fallback=await self.db.get_setting('premium_emoji_fallback','✨'); entities=[]
    if eid and fallback in text:
     off=text.index(fallback); entities=[MessageEntity(type='custom_emoji',offset=len(text[:off].encode('utf-16-le'))//2,length=len(fallback.encode('utf-16-le'))//2,custom_emoji_id=eid)]
    if entities: await self.bot.send_message(req.user_chat_id,text,entities=entities)
    else: await self.bot.send_message(req.user_chat_id,text)
    await self.db.update_request(u.id,cid,'accepted','sent')
   except Exception: await self.db.update_request(u.id,cid,'accepted','failed')
  elif accepted: await self.db.update_request(u.id,cid,'accepted')
  return 'accepted' if accepted else 'pending'
