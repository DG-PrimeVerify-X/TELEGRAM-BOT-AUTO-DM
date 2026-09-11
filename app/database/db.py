from pathlib import Path
import aiosqlite
SCHEMA='''
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS admins(user_id INTEGER PRIMARY KEY,role TEXT NOT NULL DEFAULT 'admin',permissions TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS channels(chat_id INTEGER PRIMARY KEY,title TEXT NOT NULL,username TEXT DEFAULT '',added_at TEXT DEFAULT CURRENT_TIMESTAMP,auto_accept INTEGER DEFAULT 0,auto_dm INTEGER DEFAULT 0,auto_post INTEGER DEFAULT 1,auto_reaction INTEGER DEFAULT 0,reaction_emoji TEXT DEFAULT '👍',reaction_custom_emoji_id TEXT DEFAULT '',auto_dm_template TEXT DEFAULT '✨ Welcome {name}! Your request has been accepted.');
CREATE TABLE IF NOT EXISTS admin_channels(user_id INTEGER NOT NULL,chat_id INTEGER NOT NULL,PRIMARY KEY(user_id,chat_id));
CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,username TEXT,full_name TEXT,first_seen TEXT DEFAULT CURRENT_TIMESTAMP,last_seen TEXT DEFAULT CURRENT_TIMESTAMP,source TEXT DEFAULT 'bot',eligible INTEGER DEFAULT 1,request_count INTEGER DEFAULT 0,accepted_count INTEGER DEFAULT 0,dm_sent INTEGER DEFAULT 0,dm_failed INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,request_chat_id INTEGER,username TEXT,full_name TEXT,kind TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',requested_at TEXT DEFAULT CURRENT_TIMESTAMP,processed_at TEXT,dm_status TEXT DEFAULT 'not_sent');
CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,admin_id INTEGER,action TEXT NOT NULL,details TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS scheduled_posts(id INTEGER PRIMARY KEY AUTOINCREMENT,source_chat_id INTEGER NOT NULL,source_message_id INTEGER NOT NULL,target_type TEXT NOT NULL DEFAULT 'channel',target_chat_id INTEGER DEFAULT 0,run_at TEXT NOT NULL,status TEXT DEFAULT 'pending',created_by INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
'''
DEFAULTS={'maintenance':'0','premium_emoji_id':'','premium_emoji_fallback':'✨','owner_username':''}
class Database:
 def __init__(self,path): self.path=path
 async def init(self):
  Path(self.path).parent.mkdir(parents=True,exist_ok=True)
  async with aiosqlite.connect(self.path) as d:
   await d.executescript(SCHEMA)
   for k,v in DEFAULTS.items(): await d.execute('INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)',(k,v))
   # migrate old DBs
   for col,typ in [('username',"TEXT DEFAULT ''"),('auto_accept','INTEGER DEFAULT 0'),('auto_dm','INTEGER DEFAULT 0'),('auto_post','INTEGER DEFAULT 1'),('auto_reaction','INTEGER DEFAULT 0'),('reaction_emoji',"TEXT DEFAULT '👍'"),('reaction_custom_emoji_id',"TEXT DEFAULT ''"),('auto_dm_template',"TEXT DEFAULT '✨ Welcome {name}! Your request has been accepted.'")]:
    try: await d.execute(f'ALTER TABLE channels ADD COLUMN {col} {typ}')
    except Exception: pass
   await d.commit()
 async def get_setting(self,k,default=None):
  async with aiosqlite.connect(self.path) as d:
   c=await d.execute('SELECT value FROM settings WHERE key=?',(k,)); r=await c.fetchone(); return r[0] if r else default
 async def set_setting(self,k,v):
  async with aiosqlite.connect(self.path) as d: await d.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(k,str(v))); await d.commit()
 async def log(self,uid,action,details=''):
  async with aiosqlite.connect(self.path) as d: await d.execute('INSERT INTO activity_logs(admin_id,action,details) VALUES(?,?,?)',(uid,action,details)); await d.commit()
 async def upsert_user(self,uid,username,full_name,source='bot'):
  async with aiosqlite.connect(self.path) as d: await d.execute("INSERT INTO users(user_id,username,full_name,source) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,full_name=excluded.full_name,last_seen=CURRENT_TIMESTAMP",(uid,username,full_name,source)); await d.commit()
 async def add_request(self,uid,cid,username,full_name,kind='new'):
  async with aiosqlite.connect(self.path) as d:
   await d.execute('INSERT INTO requests(user_id,request_chat_id,username,full_name,kind) VALUES(?,?,?,?,?)',(uid,cid,username,full_name,kind))
   await d.execute("INSERT INTO users(user_id,username,full_name,source,request_count) VALUES(?,?,?,?,1) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,full_name=excluded.full_name,request_count=request_count+1,last_seen=CURRENT_TIMESTAMP",(uid,username,full_name,'join_request')); await d.commit()
 async def update_request(self,uid,cid,status,dm_status=None):
  async with aiosqlite.connect(self.path) as d:
   if dm_status is None: await d.execute("UPDATE requests SET status=?,processed_at=CURRENT_TIMESTAMP WHERE user_id=? AND request_chat_id=? AND status='pending'",(status,uid,cid))
   else: await d.execute('UPDATE requests SET status=?,processed_at=CURRENT_TIMESTAMP,dm_status=? WHERE user_id=? AND request_chat_id=?',(status,dm_status,uid,cid))
   if status=='accepted': await d.execute('UPDATE users SET accepted_count=accepted_count+1 WHERE user_id=?',(uid,))
   if dm_status=='sent': await d.execute('UPDATE users SET dm_sent=dm_sent+1 WHERE user_id=?',(uid,))
   if dm_status=='failed': await d.execute('UPDATE users SET dm_failed=dm_failed+1 WHERE user_id=?',(uid,))
   await d.commit()
 async def permissions(self,uid):
  async with aiosqlite.connect(self.path) as d:
   c=await d.execute('SELECT role,permissions FROM admins WHERE user_id=?',(uid,)); r=await c.fetchone(); return {'role':r[0],'permissions':set(filter(None,r[1].split(',')))} if r else None
 async def ensure_super_admin(self,uid):
  async with aiosqlite.connect(self.path) as d: await d.execute("INSERT INTO admins(user_id,role,permissions) VALUES(?,'superadmin','all') ON CONFLICT(user_id) DO UPDATE SET role='superadmin',permissions='all'",(uid,)); await d.commit()
 async def add_admin(self,uid,p):
  async with aiosqlite.connect(self.path) as d: await d.execute("INSERT INTO admins(user_id,role,permissions) VALUES(?,'admin',?) ON CONFLICT(user_id) DO UPDATE SET permissions=excluded.permissions",(uid,p)); await d.commit()
 async def set_permissions(self,uid,p): await self.add_admin(uid,p)
 async def remove_admin(self,uid):
  async with aiosqlite.connect(self.path) as d: await d.execute('DELETE FROM admins WHERE user_id=?',(uid,)); await d.execute('DELETE FROM admin_channels WHERE user_id=?',(uid,)); await d.commit()
 async def add_channel(self,cid,title,username=''):
  async with aiosqlite.connect(self.path) as d: await d.execute("INSERT INTO channels(chat_id,title,username) VALUES(?,?,?) ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title,username=excluded.username",(cid,title,username or '')); await d.commit()
 async def remove_channel(self,cid):
  async with aiosqlite.connect(self.path) as d: await d.execute('DELETE FROM channels WHERE chat_id=?',(cid,)); await d.execute('DELETE FROM admin_channels WHERE chat_id=?',(cid,)); await d.commit()
 async def list_channels(self):
  async with aiosqlite.connect(self.path) as d: c=await d.execute('SELECT chat_id,title,username,auto_accept,auto_dm,auto_post,auto_reaction,reaction_emoji FROM channels ORDER BY title'); return await c.fetchall()
 async def channel(self,cid):
  async with aiosqlite.connect(self.path) as d: c=await d.execute('SELECT * FROM channels WHERE chat_id=?',(cid,)); r=await c.fetchone(); return r
 async def set_channel(self,cid,key,value):
  allowed={'auto_accept','auto_dm','auto_post','auto_reaction','reaction_emoji','reaction_custom_emoji_id','auto_dm_template'}
  if key not in allowed: raise ValueError('invalid channel setting')
  async with aiosqlite.connect(self.path) as d: await d.execute(f'UPDATE channels SET {key}=? WHERE chat_id=?',(value,cid)); await d.commit()
 async def assign_channel(self,uid,cid):
  async with aiosqlite.connect(self.path) as d: await d.execute('INSERT OR IGNORE INTO admin_channels(user_id,chat_id) VALUES(?,?)',(uid,cid)); await d.commit()
 async def assigned_channels(self,uid):
  async with aiosqlite.connect(self.path) as d: c=await d.execute('SELECT c.chat_id,c.title FROM channels c JOIN admin_channels a ON a.chat_id=c.chat_id WHERE a.user_id=? ORDER BY c.title'); return await c.fetchall()
 async def has_channel_access(self,uid,cid):
  p=await self.permissions(uid)
  if p and p['role']=='superadmin': return True
  async with aiosqlite.connect(self.path) as d: c=await d.execute('SELECT 1 FROM admin_channels WHERE user_id=? AND chat_id=?',(uid,cid)); return bool(await c.fetchone())
 async def list_users(self,limit=5000):
  async with aiosqlite.connect(self.path) as d: c=await d.execute('SELECT user_id FROM users WHERE eligible=1 ORDER BY last_seen DESC LIMIT ?',(limit,)); return [x[0] for x in await c.fetchall()]
 async def pending_count(self,kind=None):
  async with aiosqlite.connect(self.path) as d:
   q='SELECT COUNT(*) FROM requests WHERE status="pending"'; args=()
   if kind: q+=' AND kind=?'; args=(kind,)
   c=await d.execute(q,args); return (await c.fetchone())[0]
 async def stats(self):
  qs={'users':'SELECT COUNT(*) FROM users','requests':'SELECT COUNT(*) FROM requests','accepted':'SELECT COUNT(*) FROM requests WHERE status="accepted"','pending':'SELECT COUNT(*) FROM requests WHERE status="pending"','dm_sent':'SELECT COUNT(*) FROM requests WHERE dm_status="sent"','dm_failed':'SELECT COUNT(*) FROM requests WHERE dm_status="failed"','scheduled':'SELECT COUNT(*) FROM scheduled_posts WHERE status="pending"'}
  async with aiosqlite.connect(self.path) as d:
   out={}
   for k,q in qs.items(): c=await d.execute(q); out[k]=(await c.fetchone())[0]
   return out
 async def save_schedule(self,src_chat,src_msg,target_type,target_chat,run_at,uid):
  async with aiosqlite.connect(self.path) as d: c=await d.execute('INSERT INTO scheduled_posts(source_chat_id,source_message_id,target_type,target_chat_id,run_at,created_by) VALUES(?,?,?,?,?,?)',(src_chat,src_msg,target_type,target_chat,run_at,uid)); await d.commit(); return c.lastrowid
 async def due_schedules(self):
  async with aiosqlite.connect(self.path) as d: c=await d.execute("SELECT id,source_chat_id,source_message_id,target_type,target_chat_id FROM scheduled_posts WHERE status='pending' AND run_at<=datetime('now')"); return await c.fetchall()
 async def mark_schedule(self,sid,status):
  async with aiosqlite.connect(self.path) as d: await d.execute('UPDATE scheduled_posts SET status=? WHERE id=?',(status,sid)); await d.commit()
 async def list_schedules(self,limit=30):
  async with aiosqlite.connect(self.path) as d: c=await d.execute('SELECT id,target_chat_id,run_at,status FROM scheduled_posts ORDER BY run_at DESC LIMIT ?',(limit,)); return await c.fetchall()
 async def cancel_schedule(self,sid):
  async with aiosqlite.connect(self.path) as d: c=await d.execute("UPDATE scheduled_posts SET status='cancelled' WHERE id=? AND status='pending'",(sid,)); await d.commit(); return c.rowcount
