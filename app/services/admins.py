from app.database.db import Database

ALL = {"requests","autodm","broadcast","posts","users","stats","settings","admins","backup","reaction","schedules"}

async def allowed(db: Database, user_id: int, permission: str) -> bool:
    p = await db.permissions(user_id)
    if not p: return False
    return p["role"] == "superadmin" or "all" in p["permissions"] or permission in p["permissions"]

async def is_super_admin(db: Database, user_id: int) -> bool:
    p = await db.permissions(user_id)
    return bool(p and p["role"] == "superadmin")

async def assigned_channels(db: Database, user_id: int, default_channel: int = 0):
    p = await db.permissions(user_id)
    if not p: return []
    if p["role"] == "superadmin":
        rows = await db.list_channels()
        if rows: return rows
        return [(default_channel, str(default_channel))] if default_channel else []
    return await db.assigned_channels(user_id)
