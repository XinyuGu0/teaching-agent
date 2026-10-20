"""手动添加styles列到templates表"""

# Historical data-maintenance script. Review paths and back up data before use.
import os as _os
import sys as _sys
from pathlib import Path as _Path
if __name__ != "__main__" or _os.getenv("ALLOW_LEGACY_MAINTENANCE") != "1":
    raise SystemExit("Historical maintenance is disabled; review paths and back up data before setting ALLOW_LEGACY_MAINTENANCE=1")
_backend = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_backend))
from dotenv import load_dotenv as _load_dotenv
_load_dotenv(_backend / ".env")

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # 检查列是否存在
        result = db.session.execute(text("PRAGMA table_info(templates)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'styles' not in columns:
            print("添加styles列到templates表...")
            db.session.execute(text("ALTER TABLE templates ADD COLUMN styles JSON"))
            db.session.commit()
            print("✓ styles列添加成功！")
        else:
            print("✓ styles列已存在，无需添加")
            
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.session.rollback()