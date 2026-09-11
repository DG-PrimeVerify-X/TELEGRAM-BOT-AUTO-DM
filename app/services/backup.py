from pathlib import Path
from datetime import datetime
import shutil
def backup_database(db_path):
    src=Path(db_path); folder=src.parent/'backups'; folder.mkdir(parents=True,exist_ok=True); target=folder/f"bot-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"; shutil.copy2(src,target); return str(target)
