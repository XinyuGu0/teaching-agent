"""修复旧版 .ppt 文档的状态为 ready"""

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

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'guowaibao.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 查看当前状态
cur.execute("SELECT id, original_filename, status FROM documents WHERE status='failed'")
rows = cur.fetchall()
print(f'Found {len(rows)} failed documents:')
for r in rows:
    print(f'  {r}')

# 修复状态为 ready
cur.execute("UPDATE documents SET status='ready' WHERE status='failed'")
updated = cur.rowcount
conn.commit()
print(f'\nUpdated {updated} document(s) to ready status')

# 验证
cur.execute("SELECT id, original_filename, status FROM documents ORDER BY created_at DESC LIMIT 5")
for r in cur.fetchall():
    print(f'  id={r[0]}, name={r[1]}, status={r[2]}')

conn.close()