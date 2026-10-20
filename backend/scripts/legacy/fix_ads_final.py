
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
cp = r'C:\Users\yejia\rag_work\fix_final.sqlite3'

shutil.copy2(src, cp)
conn = sqlite3.connect(cp)
c = conn.cursor()

# 查找所有仍包含广告关键词的记录
ad_keywords = ['tsdabear', '1yb.co', '快速入群', '红包和实物抽奖']
fixed = 0

for kw in ad_keywords:
    c.execute("SELECT id, string_value FROM embedding_metadata WHERE key='chroma:document' AND string_value LIKE ?", (f'%{kw}%',))
    rows = c.fetchall()
    print(f'关键词 "{kw}": 找到 {len(rows)} 条')
    
    for rid, content in rows:
        old_len = len(content)
        # 多种广告模式清理
        new = content
        # 模式1: 卧槽...快速入群！
        new = re.sub(r'卧槽.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式2: 还有10T...快速入群！
        new = re.sub(r'还有10T.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式3: 只 有交流和学习...快速入群！
        new = re.sub(r'只\s*有交流和学习.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式4: 毫无套路...快速入群！
        new = re.sub(r'毫无套路.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式5: 红包...快速入群！
        new = re.sub(r'红包.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式6: 加我微信...快速入群！
        new = re.sub(r'加我微信.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式7: 程序员交流群...快速入群！
        new = re.sub(r'程序员交流群.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式8: 详情：https://t.1yb.co...快速入群！
        new = re.sub(r'详情：https://t\.1yb\.co.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式9: 也可以加我微信...快速入群！
        new = re.sub(r'也可以加我微信.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式10: 绝对没有广告...快速入群！
        new = re.sub(r'绝对没有广告.*?快速入群！', '', new, flags=re.DOTALL)
        # 模式11: ...快速入群！(处理残留)
        new = re.sub(r'[，,]?\s*也可以加我微信[：:]\s*\w+\s*快速入群！', '', new, flags=re.DOTALL)
        
        # 清理残余的 tsdabear 或 1yb.co 链接
        new = re.sub(r'https?://t\.1yb\.co/\S+', '', new)
        new = re.sub(r'加我微信[：:]\s*tsdabear', '', new)
        new = re.sub(r'tsdabear', '', new)
        
        # 清理多余空白
        new = re.sub(r'\n\s*\n\s*\n', '\n\n', new).strip()
        
        if len(new) < old_len:
            c.execute('UPDATE embedding_metadata SET string_value=? WHERE id=? AND key="chroma:document"', (new, rid))
            try:
                c.execute('UPDATE embedding_fulltext_search SET string_value=? WHERE rowid=?', (new, rid))
            except:
                pass
            print(f'  id={rid}: {old_len} -> {len(new)} ✅')
            fixed += 1

conn.commit()

# 最终验证
c.execute("SELECT COUNT(*) FROM embedding_metadata WHERE key='chroma:document' AND (string_value LIKE '%卧槽%' OR string_value LIKE '%tsdabear%' OR string_value LIKE '%1yb.co%' OR string_value LIKE '%快速入群%' OR string_value LIKE '%红包%')")
remaining = c.fetchone()[0]
print(f'\n清理后仍含广告的记录: {remaining}')

conn.close()
shutil.copy2(cp, src)
os.remove(cp)
print(f'共修复 {fixed} 条，已同步回原数据库')