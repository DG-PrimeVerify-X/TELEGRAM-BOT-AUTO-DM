ALL={"requests","autodm","broadcast","posts","users","stats","settings","admins","backup","reaction","schedules","channels"}

async def allowed(db,user_id,permission):
    p=await db.permissions(user_id)
    return bool(p and (p["role"]=="superadmin" or "all" in p["permissions"] or permission in p["permissions"]))

async def is_super_admin(db,user_id):
    p=await db.permissions(user_id)
    return bool(p and p["role"]=="superadmin")

async def assigned_channels(db,user_id):
    return await db.list_channels() if await is_super_admin(db,user_id) else await db.assigned_channels(user_id)

async def channel_allowed(db,user_id,chat_id,permission):
    return await allowed(db,user_id,permission) and await db.is_assigned(user_id,chat_id)
