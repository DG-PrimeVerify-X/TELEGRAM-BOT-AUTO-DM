from aiogram import Router
from aiogram.types import CallbackQuery,FSInputFile
from app.services.admins import allowed
from app.services.backup import backup_database
router=Router()
@router.callback_query(lambda c:c.data=="backup")
async def backup(call:CallbackQuery,db,config):
    if not await allowed(db,call.from_user.id,"backup"): await call.answer("⛔ Access denied",show_alert=True); return
    try: path=backup_database(config.database_path); await call.message.answer_document(FSInputFile(path),caption="💾 Database backup"); await db.log(call.from_user.id,"database_backup",path)
    except Exception as e: await call.message.answer(f"⚠️ Backup failed: {type(e).__name__}")
    await call.answer()
