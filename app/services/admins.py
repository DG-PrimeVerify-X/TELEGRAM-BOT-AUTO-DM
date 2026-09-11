ALL={'requests','autodm','broadcast','posts','users','stats','settings','admins','backup','reaction','schedules','channels'}
async def allowed(db,uid,perm):
 p=await db.permissions(uid); return bool(p and (p['role']=='superadmin' or 'all' in p['permissions'] or perm in p['permissions']))
async def superadmin(db,uid):
 p=await db.permissions(uid); return bool(p and p['role']=='superadmin')
async def channel_allowed(db,uid,cid,perm): return await allowed(db,uid,perm) and await db.has_channel_access(uid,cid)
async def assigned_channels(db,uid):
 p=await db.permissions(uid)
 if p and p['role']=='superadmin': return await db.list_channels()
 return await db.assigned_channels(uid)
