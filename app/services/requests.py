from app.database.db import Database
class RequestService:
    def __init__(self,bot,db,channel_id): self.bot,self.db,self.channel_id=bot,db,channel_id
    async def receive_new(self,req):
        u=req.from_user; await self.db.add_request(u.id,req.user_chat_id,u.username,u.full_name,"new"); return await self.process(req)
    async def process(self,req):
        if await self.db.get_setting("maintenance","0")=="1": return "maintenance"
        accepted=False
        if await self.db.get_setting("auto_accept","0")=="1":
            try: await self.bot.approve_chat_join_request(self.channel_id,req.from_user.id); accepted=True
            except Exception: return "accept_failed"
        if accepted and await self.db.get_setting("auto_dm","0")=="1":
            name=req.from_user.full_name or "there"; template=await self.db.get_setting("auto_dm_template","✨ Welcome {name}!"); text=template.replace("{name}",name).replace("{username}",req.from_user.username or "")
            try: await self.bot.send_message(req.user_chat_id,text); await self.db.update_request(req.from_user.id,req.user_chat_id,"accepted","sent")
            except Exception: await self.db.update_request(req.from_user.id,req.user_chat_id,"accepted","failed")
        elif accepted: await self.db.update_request(req.from_user.id,req.user_chat_id,"accepted")
        return "accepted" if accepted else "pending"
    async def import_pending_as_old(self): return 0
