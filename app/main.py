import asyncio,logging
from aiogram import Bot,Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import load_config
from app.database.db import Database
from app.services.requests import RequestService
from app.services.broadcast import BroadcastService
from app.services.posts import PostService
from app.services.prediction import PredictionService
from app.handlers import start,requests,settings,post,broadcast,admins,stats,health,backup,reaction,premium,channels,prediction

async def main():
    logging.basicConfig(level=logging.INFO)
    config=load_config(); db=Database(config.database_path); await db.init()
    await db.ensure_super_admin(config.super_admin_id)
    if config.owner_username: await db.set_setting("owner_username",config.owner_username)
    bot=Bot(config.bot_token,default=DefaultBotProperties(parse_mode="HTML"))
    request_service=RequestService(bot,db)
    broadcast_service=BroadcastService(bot,db)
    post_service=PostService(bot,db)
    prediction_service=PredictionService(bot,db)
    dp=Dispatcher(storage=MemoryStorage())
    dp["db"]=db; dp["config"]=config; dp["request_service"]=request_service
    dp["broadcast_service"]=broadcast_service; dp["post_service"]=post_service; dp["prediction_service"]=prediction_service
    for r in (start.router,channels.router,requests.router,settings.router,post.router,broadcast.router,admins.router,
              stats.router,health.router,backup.router,reaction.router,premium.router,prediction.router): dp.include_router(r)
    scheduler=AsyncIOScheduler(timezone=config.timezone)
    async def run_schedules():
        for sid,src,mid,tt,tc in await db.due_schedules():
            try:
                if tt=="all_users": await post_service.copy_to_all_users(src,mid)
                else: await post_service.copy_saved(src,mid,tc)
                await db.mark_schedule(sid,"completed")
            except Exception:
                logging.exception("schedule %s failed",sid); await db.mark_schedule(sid,"failed")
    scheduler.add_job(run_schedules,"interval",seconds=15,id="scheduled_posts",replace_existing=True)
    scheduler.add_job(prediction_service.tick,"interval",seconds=10,id="prediction_tick",replace_existing=True)
    scheduler.start()
    try: await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False); await prediction_service.close(); await bot.session.close()
if __name__=="__main__": asyncio.run(main())
