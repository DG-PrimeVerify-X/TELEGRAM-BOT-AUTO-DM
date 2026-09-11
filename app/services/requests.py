from aiogram.types import MessageEntity
class RequestService:
    def __init__(self,bot,db): self.bot,self.db=bot,db

    async def receive_new(self,req):
        u=req.from_user; cid=req.chat.id
        await self.db.add_request(u.id,req.user_chat_id,u.username,u.full_name,"new")
        return await self.process(req)

    async def process(self,req):
        cid=req.chat.id
        ch=await self.db.get_channel(cid)
        if not ch: return "unregistered"
        if await self.db.get_setting("maintenance","0")=="1": return "maintenance"
        accepted=False
        if ch[3]:
            try:
                await self.bot.approve_chat_join_request(cid,req.from_user.id); accepted=True
            except Exception:
                return "accept_failed"
        if accepted and ch[4]:
            name=req.from_user.full_name or "there"
            text=(ch[10] or "✨ Welcome {name}! Your request has been accepted.").replace("{name}",name).replace("{username}",req.from_user.username or "")
            emoji_id=await self.db.get_setting("premium_emoji_id","")
            fallback=await self.db.get_setting("premium_emoji_fallback","✨")
            try:
                if emoji_id and fallback in text:
                    off=text.index(fallback)
                    entity=MessageEntity(type="custom_emoji",offset=len(text[:off].encode("utf-16-le"))//2,
                                         length=len(fallback.encode("utf-16-le"))//2,custom_emoji_id=emoji_id)
                    await self.bot.send_message(req.user_chat_id,text,entities=[entity])
                else:
                    await self.bot.send_message(req.user_chat_id,text)
                await self.db.update_request(req.from_user.id,cid,"accepted","sent")
            except Exception:
                await self.db.update_request(req.from_user.id,cid,"accepted","failed")
        elif accepted:
            await self.db.update_request(req.from_user.id,cid,"accepted")
        return "accepted" if accepted else "pending"
