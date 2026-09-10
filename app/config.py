import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    super_admin_id: int
    channel_id: int
    database_path: str
    timezone: str

def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "PUT_BOT_TOKEN_HERE":
        raise RuntimeError("BOT_TOKEN is missing in .env")
    try:
        admin_id = int(os.environ["SUPER_ADMIN_ID"])
        channel_id = int(os.environ.get("CHANNEL_ID", "0"))
    except (KeyError, ValueError):
        raise RuntimeError("SUPER_ADMIN_ID must be numeric; CHANNEL_ID may be numeric or 0")
    return Config(token, admin_id, channel_id, os.getenv("DATABASE_PATH", "data/bot.db"), os.getenv("TIMEZONE", "Asia/Kolkata"))
