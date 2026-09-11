from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from app.services.admins import allowed,ALL
router=Router()
@router.callback_query(lambda c:c.data=='admins:help')
async def help(c:CallbackQuery,db):
 if not await allowed(db,c.from_user.id,'admins'): return await c.answer('🔒 Access required.',show_alert=True)
 await c.message.answer('👨‍💼 <b>Admin Manager</b>\n\n/addadmin USER_ID permissions\n/setperms USER_ID permissions\n/removeadmin USER_ID\n/assignchannel ADMIN_ID CHANNEL_ID\n/listadmins\n/listchannels\n\nPermissions: '+','.join(sorted(ALL))); await c.answer()
@router.message(Command('addadmin'))
async def add(m,db):
 if not await allowed(db,m.from_user.id,'admins'): return
 p=m.text.split(maxsplit=2); perms=p[2].replace(' ','') if len(p)>2 else 'stats'
 if len(p)<2 or not p[1].isdigit() or (perms!='all' and not set(perms.split(','))<=ALL): return await m.answer('Usage: /addadmin USER_ID permissions')
 await db.add_admin(int(p[1]),perms); await m.answer('✅ Admin added/updated.')
@router.message(Command('setperms'))
async def setp(m,db):
 if not await allowed(db,m.from_user.id,'admins'): return
 p=m.text.split(maxsplit=2); perms=p[2].replace(' ','') if len(p)==3 else ''
 if len(p)!=3 or not p[1].isdigit() or (perms!='all' and not set(perms.split(','))<=ALL): return await m.answer('Usage: /setperms USER_ID perm1,perm2')
 await db.set_permissions(int(p[1]),perms); await m.answer('✅ Permissions updated.')
@router.message(Command('removeadmin'))
async def rem(m,db):
 if not await allowed(db,m.from_user.id,'admins'): return
 p=m.text.split();
 if len(p)!=2 or not p[1].isdigit(): return await m.answer('Usage: /removeadmin USER_ID')
 await db.remove_admin(int(p[1])); await m.answer('🗑️ Admin removed.')
@router.message(Command('listadmins'))
async def la(m,db):
 if not await allowed(db,m.from_user.id,'admins'): return
 import aiosqlite
 async with aiosqlite.connect(db.path) as d: c=await d.execute('SELECT user_id,role,permissions FROM admins ORDER BY role,user_id'); rows=await c.fetchall()
 await m.answer('👨‍💼 <b>Admins</b>\n\n'+('\n'.join(f'<code>{u}</code> • {r} • {p}' for u,r,p in rows) or 'None'))
@router.message(Command('listchannels'))
async def lc(m,db):
 if not await allowed(db,m.from_user.id,'channels'): return
 rows=await db.list_channels(); await m.answer('📢 <b>Channels</b>\n\n'+('\n'.join(f'<code>{r[0]}</code> • {r[1]}' for r in rows) or 'None'))
