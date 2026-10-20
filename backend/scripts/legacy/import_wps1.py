
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

import os, shutil, sqlite3, uuid

src = r'd:\study\项目\国外包2\guowaibao_ys\backend\data\vector_db\chroma.sqlite3'
cp = r'C:\Users\yejia\rag_work\import_wps1.sqlite3'

WPS1_CONTENT = """[图片类型]: PNG图片
[AI分析内容]:
这张图展示了完整的数据库系统层次架构，从最内层到最外层依次为硬件与数据库、操作系统、数据库管理系统、应用开发工具软件、应用系统，最终面向数据库用户；其中硬件与数据库是整个体系的物理与数据基础，操作系统负责管理和调度硬件资源、提供基础运行支撑，数据库管理系统承担数据的统一管理与核心调度功能，应用开发工具软件为业务开发提供技术支撑，在此基础上搭建各类面向业务的应用系统，最终由数据库用户直接操作使用上层应用，形成了自下而上逐层支撑、逐层封装的数据库系统服务体系。"""

shutil.copy2(src, cp)
conn = sqlite3.connect(cp)
c = conn.cursor()

# 获取 segment_id
c.execute("SELECT DISTINCT segment_id FROM embeddings LIMIT 1")
segment_id = c.fetchone()[0]

# 获取最大 id
c.execute("SELECT MAX(id) FROM embeddings")
max_id = c.fetchone()[0]

new_id = max_id + 1
doc_uuid = str(uuid.uuid4())
embedding_id = f"{doc_uuid}_chunk_0"
user_id = "a727de8f-c791-47e1-908a-9ae7002b550f"

# 插入 embeddings
c.execute("INSERT INTO embeddings (id, segment_id, embedding_id, seq_id) VALUES (?, ?, ?, ?)",
          (new_id, segment_id, embedding_id, new_id))

# 插入 metadata
for key, val in [
    ('chroma:document', WPS1_CONTENT),
    ('document_id', doc_uuid),
    ('user_id', user_id),
    ('filename', 'wps1.png'),
    ('file_type', 'image'),
    ('chunk_index', '0'),
    ('total_chunks', '1'),
]:
    c.execute("INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, ?, ?)", (new_id, key, val))

# 插入 FTS
c.execute("INSERT INTO embedding_fulltext_search (rowid, string_value) VALUES (?, ?)", (new_id, WPS1_CONTENT))

conn.commit()

# 验证
c.execute("SELECT COUNT(*) FROM embeddings")
total = c.fetchone()[0]
c.execute("SELECT string_value FROM embedding_metadata WHERE id=? AND key='filename'", (new_id,))
fn = c.fetchone()[0]
print(f'✅ wps1.png 已导入 (id={new_id}, filename={fn})')
print(f'总记录数: {total}')

conn.close()
shutil.copy2(cp, src)
os.remove(cp)
print('Done!')