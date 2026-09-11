import asyncio,logging
from aiogram import Bot,Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import load_config
from app.database.db import Database
from app.services.requests import RequestService
from app.services.broadcast import BroadcastService
from app.services.posts import PostService
from app.handlers import start,requests,settings,post,broadcast,admins,stats,health,backup,reaction,premium,channels
async def main():
 logging.basicConfig(level=logging.INFO)
 cfg=load_config(); db=Database(cfg.database_path); await db.init(); await db.ensure_super_admin(cfg.super_admin_id)
 if not await db.get_setting('owner_username',''): await db.set_setting('owner_username',cfg.owner_username)
 bot=Bot(cfg.bot_token); req=RequestService(bot,db); b=BroadcastService(bot,db); ps=PostService(bot,db)
 dp=Dispatcher(storage=MemoryStorage()); dp['db']=db; dp['config']=cfg
 for r in (start.router,channels.router,requests.router,settings.router,post.router,broadcast.router,admins.router,stats.router,health.router,backup.router,reaction.router,premium.router): dp.include_router(r)
 scheduler=AsyncIOScheduler(timezone=cfg.timezone)
 async def jobs():
  for sid,src,mid,typ,target in await db.due_schedules():
   try:
    if typ=='all_users': await ps.copy_to_all_users(src,mid)
    else: await ps.copy_saved(src,mid,target)
    await db.mark_schedule(sid,'completed')
   except Exception: await db.mark_schedule(sid,'failed')
 scheduler.add_job(jobs,'interval',seconds=15,id='scheduler',replace_existing=True); scheduler.start()
 try: await dp.start_polling(bot,db=db,config=cfg,request_service=req,broadcast_service=b,post_service=ps)
 finally: scheduler.shutdown(wait=False); await bot.session.close()
if __name__=='__main__': asyncio.run(main())
