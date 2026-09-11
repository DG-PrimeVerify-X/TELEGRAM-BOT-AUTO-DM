import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
class BroadcastService:
    def __init__(self,bot,db): self.bot,self.db=bot,db; self.running=False
    async def copy_message(self,source_chat_id,source_message_id,user_ids,delay=.08):
        self.running=True; sent=failed=0
        for uid in user_ids:
            if not self.running: break
            try: await self.bot.copy_message(chat_id=uid,from_chat_id=source_chat_id,message_id=source_message_id); sent+=1
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                try: await self.bot.copy_message(chat_id=uid,from_chat_id=source_chat_id,message_id=source_message_id); sent+=1
                except Exception: failed+=1
            except Exception: failed+=1
            await asyncio.sleep(delay)
        self.running=False; return sent,failed
    def stop(self): self.running=False
