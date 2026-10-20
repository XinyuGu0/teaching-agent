
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
cp = r'C:\Users\yejia\rag_work\fix_all_ads.sqlite3'

shutil.copy2(src, cp)
conn = sqlite3.connect(cp)
c = conn.cursor()

# 查找所有包含广告的记录
c.execute("SELECT id, string_value FROM embedding_metadata WHERE key='chroma:document' AND string_value LIKE '%卧槽%'")
rows = c.fetchall()
print(f'找到 {len(rows)} 条包含广告的记录')

fixed = 0
for rid, content in rows:
    old_len = len(content)
    # 用正则删除广告
    new = re.sub(r'卧槽.*?快速入群！', '', content, flags=re.DOTALL)
    new = re.sub(r'\n\s*\n\s*\n', '\n\n', new).strip()
    
    if len(new) < old_len:
        c.execute('UPDATE embedding_metadata SET string_value=? WHERE id=? AND key="chroma:document"', (new, rid))
        try:
            c.execute('UPDATE embedding_fulltext_search SET string_value=? WHERE rowid=?', (new, rid))
        except:
            pass
        print(f'  id={rid}: {old_len} -> {len(new)} 字符 ✅')
        fixed += 1
    else:
        print(f'  id={rid}: 未变化')

conn.commit()

# 验证
c.execute("SELECT COUNT(*) FROM embedding_metadata WHERE key='chroma:document' AND string_value LIKE '%卧槽%'")
remaining = c.fetchone()[0]
print(f'\n清理后仍含广告的记录: {remaining}')

conn.close()
shutil.copy2(cp, src)
os.remove(cp)
print(f'共修复 {fixed} 条记录，已同步回原数据库')