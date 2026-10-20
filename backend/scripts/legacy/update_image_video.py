"""
更新知识库中的图片内容和视频记录
仅通过 SQLite 操作，不使用 ChromaDB（避免 HNSW 崩溃）
"""

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

import os
import shutil
import sqlite3

REAL_VECTOR_DB = r"d:\study\项目\国外包2\guowaibao_ys\backend\data\vector_db"
WORK_COPY = r"C:\Users\yejia\rag_work\work_update.sqlite3"

IMAGE_CONTENTS = {
    "16ER模型.png": """[图片类型]: PNG图片
[AI分析内容]:
仓库管理系统 E-R 数据模型中，包含企业、管理员、客户、采购员、库房、商品六大核心实体，其中企业拥有编号、名称属性，管理员拥有编号、姓名属性，客户拥有编号、姓名属性，采购员拥有姓名、性别属性，库房拥有编号、类别属性，商品拥有编号、名称属性；实体间通过多类联系关联：一个企业可管理 M 个管理员、O 个客户、N 个采购员，管理员以一对多的关系管理库房，库房、客户与商品之间存在带名称、日期属性的出库联系，采购员与商品之间存在带名称、日期属性的多对多采购联系，库房与商品之间还存在带编号、名称属性的一对多入库联系。""",

    "15ER模型.png": """[图片类型]: PNG图片
[AI分析内容]:
医院管理 E-R 数据模型包含医院、科室、医生、病房、患者、药品六大实体，医院具备编号、名称属性，科室具备编号、名称属性，医生具备编号、姓名属性，病房具备编号、名称属性，患者具备患者编号、患者姓名属性，药品具备药品编号、药品名称属性；实体间依靠组成、住院、开药三类联系连接：一家医院可组成 N 个科室，一个科室可组成 N 名医生、若干病房，医生、病房与患者之间构成 M:O:N 的住院联系，附带医生编号、患者编号标识，医生、患者与药品之间存在多实体开药联系，实现医生为患者开具对应药品的业务逻辑。"""
}

def main():
    print("=" * 60)
    print("更新知识库 - 图片内容 & 视频记录处理 (纯SQLite)")
    print("=" * 60)

    src_db = os.path.join(REAL_VECTOR_DB, "chroma.sqlite3")
    if os.path.exists(WORK_COPY):
        os.remove(WORK_COPY)
    shutil.copy2(src_db, WORK_COPY)
    print(f"✅ 已复制数据库到: {WORK_COPY}")

    conn = sqlite3.connect(WORK_COPY)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # 查找记录
    cur.execute("SELECT id, string_value FROM embedding_metadata WHERE key='filename' AND string_value IN ('SQL.mp4','15ER模型.png','16ER模型.png')")
    records = cur.fetchall()
    print(f"\n找到 {len(records)} 条记录:")
    record_map = {}
    for rid, fn in records:
        print(f"  id={rid}, filename={fn}")
        record_map[fn] = rid

    # 1. 删除视频
    if "SQL.mp4" in record_map:
        video_id = record_map["SQL.mp4"]
        print(f"\n📹 删除视频 SQL.mp4 (id={video_id}):")
        
        # 先查看完整记录
        cur.execute("SELECT * FROM embeddings WHERE id=?", (video_id,))
        emb_row = cur.fetchone()
        if emb_row:
            print(f"  embeddings: {emb_row}")
            
            cur.execute("DELETE FROM embeddings WHERE id=?", (video_id,))
            print(f"  ✅ 已删除 embeddings 记录")
        
        cur.execute("DELETE FROM embedding_metadata WHERE id=?", (video_id,))
        print(f"  ✅ 已删除 embedding_metadata 记录")
        
        try:
            cur.execute("DELETE FROM embedding_fulltext_search WHERE rowid=?", (video_id,))
            print(f"  ✅ 已删除 FTS 记录")
        except Exception as e:
            print(f"  ⚠️ FTS: {e}")
        
        try:
            cur.execute("DELETE FROM embedding_metadata_array WHERE id=?", (video_id,))
            print(f"  ✅ 已删除 metadata_array 记录")
        except Exception as e:
            print(f"  ⚠️ metadata_array: {e}")

    # 2. 更新图片
    for filename, content in IMAGE_CONTENTS.items():
        if filename not in record_map:
            print(f"\n⚠️ 未找到 {filename}，跳过")
            continue

        img_id = record_map[filename]
        print(f"\n🖼️ 更新 {filename} (id={img_id}):")
        print(f"  新内容长度: {len(content)} 字符")

        # 更新文档内容
        cur.execute(
            "UPDATE embedding_metadata SET string_value=? WHERE id=? AND key='chroma:document'",
            (content, img_id)
        )
        updated = cur.rowcount
        print(f"  ✅ chroma:document 已更新 (影响 {updated} 行)")

        # 更新 FTS
        try:
            cur.execute("UPDATE embedding_fulltext_search SET string_value=? WHERE rowid=?",
                       (content, img_id))
            print(f"  ✅ FTS 已更新")
        except Exception as e:
            print(f"  ⚠️ FTS 更新失败: {e}")

    # 检查总记录数
    cur.execute("SELECT COUNT(*) FROM embeddings")
    total = cur.fetchone()[0]
    print(f"\n📊 更新后 embeddings 总记录数: {total}")

    conn.commit()
    conn.close()
    print(f"✅ SQLite 操作完成")

    # 复制回原路径
    shutil.copy2(WORK_COPY, src_db)
    print(f"✅ 数据库已复制回原路径")

    # 清理
    os.remove(WORK_COPY)
    print(f"✅ 临时文件已清理")

    print(f"\n{'=' * 60}")
    print(f"操作完成！")
    print(f"  - 视频 SQL.mp4: 已删除")
    print(f"  - 15ER模型.png: 文本内容已更新")
    print(f"  - 16ER模型.png: 文本内容已更新")
    print(f"  ⚠️ 注意: embedding向量未更新（HNSW库崩溃），文本搜索已生效")

if __name__ == "__main__":
    main()