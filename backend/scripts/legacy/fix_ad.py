
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

import os, shutil, sqlite3, re

src = r'd:\study\项目\国外包2\guowaibao_ys\backend\data\vector_db\chroma.sqlite3'
cp = r'C:\Users\yejia\rag_work\fix_ad2.sqlite3'

shutil.copy2(src, cp)
conn = sqlite3.connect(cp)
c = conn.cursor()

c.execute('SELECT string_value FROM embedding_metadata WHERE id=210 AND key="chroma:document"')
row = c.fetchone()
old = row[0]
print(f'Old length: {len(old)}')
print(f'Old start: {repr(old[:100])}')

# 用正则删除广告 - 匹配 "卧槽" 到 "快速入群！" 之间的所有内容
new = re.sub(r'卧槽.*?快速入群！', '', old, flags=re.DOTALL)
# 清理多余空白
new = re.sub(r'\n\s*\n\s*\n', '\n\n', new).strip()

print(f'New length: {len(new)}')
print(f'New start: {repr(new[:200])}')

# 检查广告是否还在
if '卧槽' in new:
    print('WARNING: Ad text still present!')
else:
    print('SUCCESS: Ad text removed!')

c.execute('UPDATE embedding_metadata SET string_value=? WHERE id=210 AND key="chroma:document"', (new,))
c.execute('UPDATE embedding_fulltext_search SET string_value=? WHERE rowid=210', (new,))
conn.commit()

# 验证
c.execute('SELECT string_value FROM embedding_metadata WHERE id=210 AND key="chroma:document"')
verify = c.fetchone()[0]
print(f'Verify length: {len(verify)}')
print(f'Verify start: {repr(verify[:200])}')

conn.close()

shutil.copy2(cp, src)
os.remove(cp)
print('Database updated and copied back!')