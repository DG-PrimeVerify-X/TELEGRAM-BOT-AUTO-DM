import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
@dataclass(frozen=True)
class Config:
    bot_token:str; super_admin_id:int; database_path:str; timezone:str; owner_username:str

def load_config()->Config:
    token=os.getenv('BOT_TOKEN','').strip()
    if not token: raise RuntimeError('BOT_TOKEN is missing in .env')
    try: sid=int(os.environ['SUPER_ADMIN_ID'])
    except (KeyError,ValueError): raise RuntimeError('SUPER_ADMIN_ID must be numeric')
    return Config(token,sid,os.getenv('DATABASE_PATH','data/bot.db'),os.getenv('TIMEZONE','Asia/Kolkata'),os.getenv('OWNER_USERNAME','DGPrimeVerifyX').lstrip('@'))
