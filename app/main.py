import asyncio,logging
from aiogram import Bot,Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import load_config
from app.database.db import Database
from app.services.requests import RequestService
from app.services.broadcast import BroadcastService
from app.services.posts import PostService
from app.keyboards.admin import main_menu
from app.handlers import start,requests,settings,post,broadcast,admins,stats,health,backup,reaction,premium,premium

async def main():
    logging.basicConfig(level=logging.INFO)
    config=load_config(); db=Database(config.database_path); await db.init()
    await db.ensure_super_admin(config.super_admin_id)
    bot=Bot(config.bot_token)
    req=RequestService(bot,db,config.channel_id); bcast=BroadcastService(bot,db); posts=PostService(bot,db)
    if config.channel_id:
        try:
            chat=await bot.get_chat(config.channel_id); await db.add_channel(config.channel_id,chat.title or str(config.channel_id))
        except Exception: pass
    dp=Dispatcher(storage=MemoryStorage()); dp["db"]=db; dp["config"]=config
    for r in (start.router,requests.router,settings.router,post.router,broadcast.router,admins.router,stats.router,health.router,backup.router,reaction.router,premium.router): dp.include_router(r)
    scheduler=AsyncIOScheduler(timezone=config.timezone)
    async def run_schedules():
        for row in await db.due_schedules():
            sid,src_chat,src_msg,target_type,target_chat=row
            try:
                if target_type=="all_users": await posts.copy_to_all_users(src_chat,src_msg)
                else: await posts.copy_saved(src_chat,src_msg,target_chat)
                await db.mark_schedule(sid,"completed")
            except Exception as e:
                logging.exception("schedule %s failed",sid); await db.mark_schedule(sid,"failed")
    scheduler.add_job(run_schedules,"interval",seconds=15,id="scheduled_posts",replace_existing=True); scheduler.start()
    try: await dp.start_polling(bot,db=db,config=config,request_service=req,broadcast_service=bcast,post_service=posts)
    finally: scheduler.shutdown(wait=False); await bot.session.close()
if __name__=="__main__": asyncio.run(main())
