from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.services.admins import allowed, ALL

router = Router()

@router.callback_query(lambda c: c.data == "admins:help")
async def help_admins(call: CallbackQuery, db):
    if not await allowed(db, call.from_user.id, "admins"):
        await call.answer("⛔ Access denied", show_alert=True); return
    text = ("👨‍💼 <b>Admin & Channel Commands</b>\n\n"
            "<code>/addadmin USER_ID permissions</code>\n"
            "<code>/setperms USER_ID permissions</code>\n"
            "<code>/removeadmin USER_ID</code>\n"
            "<code>/addchannel CHANNEL_ID</code>\n"
            "<code>/removechannel CHANNEL_ID</code>\n"
            "<code>/assignchannel ADMIN_ID CHANNEL_ID</code>\n"
            "<code>/listadmins</code>\n<code>/listchannels</code>\n\n"
            "Permissions: " + ", ".join(sorted(ALL)))
    await call.message.answer(text); await call.answer()

@router.message(Command("addadmin"))
async def addadmin(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    p = message.text.split(maxsplit=2)
    if len(p) < 2 or not p[1].isdigit(): await message.answer("Usage: /addadmin USER_ID permissions"); return
    perms = p[2].replace(" ", "") if len(p) > 2 else "stats"
    if perms != "all" and not set(perms.split(",")) <= ALL:
        await message.answer("⚠️ Invalid permission."); return
    await db.add_admin(int(p[1]), perms); await message.answer(f"✅ Admin <code>{p[1]}</code> added/updated.")

@router.message(Command("setperms"))
async def setperms(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    p = message.text.split(maxsplit=2)
    perms = p[2].replace(" ", "") if len(p) == 3 else ""
    if len(p) != 3 or not p[1].isdigit() or (perms != "all" and not set(perms.split(",")) <= ALL):
        await message.answer("Usage: /setperms USER_ID perm1,perm2"); return
    await db.set_permissions(int(p[1]), perms); await message.answer("✅ Permissions updated.")

@router.message(Command("removeadmin"))
async def removeadmin(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    p = message.text.split()
    if len(p) != 2 or not p[1].isdigit(): await message.answer("Usage: /removeadmin USER_ID"); return
    await db.remove_admin(int(p[1])); await message.answer("🗑️ Admin removed.")

@router.message(Command("addchannel"))
async def addchannel(message: Message, db, bot):
    if not await allowed(db, message.from_user.id, "admins"): return
    p = message.text.split()
    if len(p) != 2: await message.answer("Usage: /addchannel CHANNEL_ID"); return
    try:
        cid = int(p[1]); chat = await bot.get_chat(cid)
        await db.add_channel(cid, chat.title or str(cid)); await message.answer(f"✅ Channel added: <b>{chat.title}</b> (<code>{cid}</code>)")
    except Exception as e: await message.answer(f"⚠️ Could not add channel: <code>{type(e).__name__}</code>")

@router.message(Command("removechannel"))
async def removechannel(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    p = message.text.split()
    if len(p) != 2: await message.answer("Usage: /removechannel CHANNEL_ID"); return
    await db.remove_channel(int(p[1])); await message.answer("🗑️ Channel removed.")

@router.message(Command("assignchannel"))
async def assignchannel(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    p = message.text.split()
    if len(p) != 3 or not p[1].lstrip('-').isdigit() or not p[2].lstrip('-').isdigit():
        await message.answer("Usage: /assignchannel ADMIN_ID CHANNEL_ID"); return
    cid = int(p[2])
    if cid not in [x[0] for x in await db.list_channels()]:
        await message.answer("⚠️ Channel is not registered. Use /addchannel first."); return
    await db.assign_channel(int(p[1]), cid); await message.answer("✅ Channel assigned.")

@router.message(Command("listchannels"))
async def listchannels(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    rows = await db.list_channels()
    text = "📢 <b>Channels</b>\n\n" + ("\n".join(f"{i+1}. {t} — <code>{c}</code>" for i,(c,t) in enumerate(rows)) if rows else "No channels registered.")
    await message.answer(text)

@router.message(Command("listadmins"))
async def listadmins(message: Message, db):
    if not await allowed(db, message.from_user.id, "admins"): return
    import aiosqlite
    async with aiosqlite.connect(db.path) as con:
        cur = await con.execute("SELECT user_id,role,permissions FROM admins ORDER BY role,user_id"); rows = await cur.fetchall()
    await message.answer("👨‍💼 <b>Admins</b>\n\n" + ("\n".join(f"<code>{u}</code> • {r} • {p}" for u,r,p in rows) if rows else "No admins."))
