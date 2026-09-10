from pathlib import Path
import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS admins(user_id INTEGER PRIMARY KEY, role TEXT NOT NULL DEFAULT 'admin', permissions TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS channels(chat_id INTEGER PRIMARY KEY, title TEXT NOT NULL, added_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS admin_channels(user_id INTEGER NOT NULL, chat_id INTEGER NOT NULL, PRIMARY KEY(user_id,chat_id));
CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT, first_seen TEXT DEFAULT CURRENT_TIMESTAMP, last_seen TEXT DEFAULT CURRENT_TIMESTAMP, source TEXT DEFAULT 'bot', eligible INTEGER DEFAULT 1, request_count INTEGER DEFAULT 0, accepted_count INTEGER DEFAULT 0, dm_sent INTEGER DEFAULT 0, dm_failed INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,request_chat_id INTEGER,username TEXT,full_name TEXT,kind TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',requested_at TEXT DEFAULT CURRENT_TIMESTAMP,processed_at TEXT,dm_status TEXT DEFAULT 'not_sent');
CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,admin_id INTEGER,action TEXT NOT NULL,details TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS scheduled_posts(id INTEGER PRIMARY KEY AUTOINCREMENT,source_chat_id INTEGER NOT NULL,source_message_id INTEGER NOT NULL,target_type TEXT NOT NULL DEFAULT 'channel',target_chat_id INTEGER DEFAULT 0,run_at TEXT NOT NULL,status TEXT DEFAULT 'pending',created_by INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""
DEFAULTS={"auto_accept":"0","auto_dm":"0","maintenance":"0","auto_dm_template":"✨ Welcome {name}! Your request has been accepted.","auto_reaction":"0","reaction_emoji":"👍","premium_emoji_id":"","premium_emoji_fallback":"✨"}

class Database:
    def __init__(self,path): self.path=path
    async def init(self):
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(SCHEMA)
            try: await db.execute("ALTER TABLE scheduled_posts ADD COLUMN target_type TEXT NOT NULL DEFAULT 'channel'")
            except Exception: pass
            for k,v in DEFAULTS.items(): await db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",(k,v))
            await db.commit()
    async def get_setting(self,key,default=None):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT value FROM settings WHERE key=?",(key,)); row=await cur.fetchone(); return row[0] if row else default
    async def set_setting(self,key,value):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,str(value))); await db.commit()
    async def log(self,admin_id,action,details=""):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO activity_logs(admin_id,action,details) VALUES(?,?,?)",(admin_id,action,details)); await db.commit()
    async def upsert_user(self,user_id,username,full_name,source="bot"):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO users(user_id,username,full_name,source) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,full_name=excluded.full_name,last_seen=CURRENT_TIMESTAMP",(user_id,username,full_name,source)); await db.commit()
    async def add_request(self,user_id,request_chat_id,username,full_name,kind):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO requests(user_id,request_chat_id,username,full_name,kind) VALUES(?,?,?,?,?)",(user_id,request_chat_id,username,full_name,kind))
            await db.execute("INSERT INTO users(user_id,username,full_name,source,request_count) VALUES(?,?,?,?,1) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,full_name=excluded.full_name,request_count=request_count+1,last_seen=CURRENT_TIMESTAMP",(user_id,username,full_name,"join_request")); await db.commit()
    async def update_request(self,user_id,request_chat_id,status,dm_status=None):
        async with aiosqlite.connect(self.path) as db:
            if dm_status is None: await db.execute("UPDATE requests SET status=?,processed_at=CURRENT_TIMESTAMP WHERE user_id=? AND request_chat_id=? AND status='pending'",(status,user_id,request_chat_id))
            else: await db.execute("UPDATE requests SET status=?,processed_at=CURRENT_TIMESTAMP,dm_status=? WHERE user_id=? AND request_chat_id=?",(status,dm_status,user_id,request_chat_id))
            if status=="accepted": await db.execute("UPDATE users SET accepted_count=accepted_count+1 WHERE user_id=?",(user_id,))
            if dm_status=="sent": await db.execute("UPDATE users SET dm_sent=dm_sent+1 WHERE user_id=?",(user_id,))
            if dm_status=="failed": await db.execute("UPDATE users SET dm_failed=dm_failed+1 WHERE user_id=?",(user_id,))
            await db.commit()
    async def pending_count(self,kind=None):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT COUNT(*) FROM requests WHERE status='pending'" + (" AND kind=?" if kind else ""),((kind,) if kind else ())); return (await cur.fetchone())[0]
    async def stats(self):
        async with aiosqlite.connect(self.path) as db:
            out={}
            for k,q in {"users":"SELECT COUNT(*) FROM users","new_requests":"SELECT COUNT(*) FROM requests WHERE kind='new'","old_requests":"SELECT COUNT(*) FROM requests WHERE kind='old'","accepted":"SELECT COUNT(*) FROM requests WHERE status='accepted'","pending":"SELECT COUNT(*) FROM requests WHERE status='pending'","dm_sent":"SELECT COUNT(*) FROM requests WHERE dm_status='sent'","dm_failed":"SELECT COUNT(*) FROM requests WHERE dm_status='failed'","scheduled":"SELECT COUNT(*) FROM scheduled_posts WHERE status='pending'"}.items():
                cur=await db.execute(q); out[k]=(await cur.fetchone())[0]
            return out
    async def list_users(self,limit=5000):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT user_id FROM users WHERE eligible=1 ORDER BY last_seen DESC LIMIT ?",(limit,)); return [r[0] for r in await cur.fetchall()]
    async def permissions(self,user_id):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT role,permissions FROM admins WHERE user_id=?",(user_id,)); row=await cur.fetchone()
            if not row:return None
            return {"role":row[0],"permissions":set(filter(None,row[1].split(",")))}
    async def ensure_super_admin(self,user_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO admins(user_id,role,permissions) VALUES(?,'superadmin','all') ON CONFLICT(user_id) DO UPDATE SET role='superadmin',permissions='all'",(user_id,)); await db.commit()
    async def ensure_super_admin(self,user_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO admins(user_id,role,permissions) VALUES(?,'superadmin','all') ON CONFLICT(user_id) DO UPDATE SET role='superadmin',permissions='all'",(user_id,)); await db.commit()
    async def add_admin(self,user_id,permissions):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO admins(user_id,role,permissions) VALUES(?, 'admin',?) ON CONFLICT(user_id) DO UPDATE SET role='admin',permissions=excluded.permissions",(user_id,permissions)); await db.commit()
    async def set_permissions(self,user_id,permissions): await self.add_admin(user_id,permissions)
    async def remove_admin(self,user_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM admins WHERE user_id=?",(user_id,)); await db.execute("DELETE FROM admin_channels WHERE user_id=?",(user_id,)); await db.commit()
    async def add_channel(self,chat_id,title):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO channels(chat_id,title) VALUES(?,?) ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title",(chat_id,title)); await db.commit()
    async def remove_channel(self,chat_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM channels WHERE chat_id=?",(chat_id,)); await db.execute("DELETE FROM admin_channels WHERE chat_id=?",(chat_id,)); await db.commit()
    async def list_channels(self):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT chat_id,title FROM channels ORDER BY title"); return await cur.fetchall()
    async def assign_channel(self,user_id,chat_id):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT OR IGNORE INTO admin_channels(user_id,chat_id) VALUES(?,?)",(user_id,chat_id)); await db.commit()
    async def assigned_channels(self,user_id):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT c.chat_id,c.title FROM channels c JOIN admin_channels a ON a.chat_id=c.chat_id WHERE a.user_id=? ORDER BY c.title",(user_id,)); return await cur.fetchall()
    async def save_schedule(self,source_chat_id,source_message_id,target_type,target_chat_id,run_at,created_by):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("INSERT INTO scheduled_posts(source_chat_id,source_message_id,target_type,target_chat_id,run_at,created_by) VALUES(?,?,?,?,?,?)",(source_chat_id,source_message_id,target_type,target_chat_id,run_at,created_by)); await db.commit(); return cur.lastrowid
    async def due_schedules(self):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT id,source_chat_id,source_message_id,target_type,target_chat_id FROM scheduled_posts WHERE status='pending' AND run_at<=datetime('now')"); return await cur.fetchall()
    async def mark_schedule(self,sid,status):
        async with aiosqlite.connect(self.path) as db: await db.execute("UPDATE scheduled_posts SET status=? WHERE id=?",(status,sid)); await db.commit()
    async def list_schedules(self,limit=30):
        async with aiosqlite.connect(self.path) as db:
            cur=await db.execute("SELECT id,target_chat_id,run_at,status FROM scheduled_posts ORDER BY run_at DESC LIMIT ?",(limit,)); return await cur.fetchall()
    async def cancel_schedule(self,sid):
        async with aiosqlite.connect(self.path) as db: cur=await db.execute("UPDATE scheduled_posts SET status='cancelled' WHERE id=? AND status='pending'",(sid,)); await db.commit(); return cur.rowcount
