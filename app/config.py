import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    super_admin_id: int
    owner_username: str
    database_path: str
    timezone: str

def load_config():
    token=os.getenv("BOT_TOKEN","").strip()
    if not token or token=="PUT_BOT_TOKEN_HERE":
        raise RuntimeError("BOT_TOKEN is missing in .env")
    try: sid=int(os.environ["SUPER_ADMIN_ID"])
    except (KeyError,ValueError): raise RuntimeError("SUPER_ADMIN_ID must be numeric")
    return Config(token,sid,os.getenv("OWNER_USERNAME","dragonb98").strip().lstrip("@"),
                  os.getenv("DATABASE_PATH","data/bot.db"),os.getenv("TIMEZONE","Asia/Kolkata"))
