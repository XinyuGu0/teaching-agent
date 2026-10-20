"""
检查 chroma.sqlite3 数据库内容
1. 打印所有文件及其内容摘要
2. 检查是否存在学校名
3. 检查是否存在不相关字段
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
WORK_COPY = r"C:\Users\yejia\rag_work\check_all.sqlite3"

# 常见学校名关键词
SCHOOL_KEYWORDS = ['大学', '学院', '学校', '校区', '师范', '理工', '工业', '农业', '医科', '财经', '政法', '民族', '外国语', '职业', '清华', '北大', '复旦', '浙大', '交大', '南大', '武大', '华科', '厦大', '中山', '人民', '科技', '航空', '石油', '矿业', '地质', '邮电', '电子', '海洋', '林业', '农业']

# 不相关内容关键词
IRRELEVANT_KEYWORDS = ['卧槽', '红包', '抽奖', '入群', '微信群', '公众号', '关注', '转发', '领取', '限时', '免费领取', '扫码', '加我微信', 'tsdabear', '1yb.co', '套路']

def main():
    src_db = os.path.join(REAL_VECTOR_DB, "chroma.sqlite3")
    shutil.copy2(src_db, WORK_COPY)
    
    conn = sqlite3.connect(WORK_COPY)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ========== 1. 打印所有文件及内容 ==========
    print("=" * 80)
    print("第一部分：所有文件及内容检查")
    print("=" * 80)
    
    # 获取所有记录的文件名
    cur.execute("""
        SELECT em.id, em.string_value as filename 
        FROM embedding_metadata em 
        WHERE em.key='filename' 
        ORDER BY em.id
    """)
    files = cur.fetchall()
    
    print(f"\n总文件记录数: {len(files)}")
    print(f"总 distinct 文件数: {len(set(f['filename'] for f in files))}")
    
    for idx, f in enumerate(files):
        rid = f['id']
        fn = f['filename']
        
        # 获取该记录的所有元数据
        cur.execute("SELECT key, string_value FROM embedding_metadata WHERE id=?", (rid,))
        metas = {r['key']: r['string_value'] for r in cur.fetchall()}
        
        doc_content = metas.get('chroma:document', '(无)')
        file_type = metas.get('file_type', '(未知)')
        chunk_idx = metas.get('chunk_index', '')
        total_chunks = metas.get('total_chunks', '')
        
        content_preview = doc_content[:200].replace('\n', '\\n') if doc_content and doc_content != '(无)' else '(无内容)'
        content_len = len(doc_content) if doc_content and doc_content != '(无)' else 0
        
        print(f"\n--- [{idx+1}/{len(files)}] id={rid} ---")
        print(f"  文件名: {fn}")
        print(f"  类型: {file_type}")
        print(f"  块: {chunk_idx}/{total_chunks}")
        print(f"  内容长度: {content_len} 字符")
        print(f"  内容预览: {content_preview}")
    
    # ========== 2. 检查学校名 ==========
    print(f"\n\n{'=' * 80}")
    print("第二部分：学校名检查")
    print("=" * 80)
    
    school_found = []
    cur.execute("SELECT id, string_value FROM embedding_metadata WHERE key='chroma:document'")
    for row in cur.fetchall():
        content = row['string_value'] or ''
        rid = row['id']
        for kw in SCHOOL_KEYWORDS:
            if kw in content:
                # 找到包含学校关键词的上下文
                idx_pos = content.find(kw)
                context = content[max(0,idx_pos-20):idx_pos+30].replace('\n', ' ')
                # 获取文件名
                cur2 = conn.cursor()
                cur2.execute("SELECT string_value FROM embedding_metadata WHERE id=? AND key='filename'", (rid,))
                fn_row = cur2.fetchone()
                filename = fn_row[0] if fn_row else '未知'
                school_found.append((filename, kw, context))
    
    if school_found:
        print(f"\n⚠️ 发现 {len(school_found)} 处可能包含学校名称的内容:")
        seen = set()
        for fn, kw, ctx in school_found:
            key = f"{fn}|{kw}|{ctx}"
            if key not in seen:
                seen.add(key)
                print(f"  文件: {fn}")
                print(f"  关键词: {kw}")
                print(f"  上下文: ...{ctx}...")
                print()
    else:
        print("\n✅ 未发现学校名称相关内容")

    # ========== 3. 检查不相关内容 ==========
    print(f"\n{'=' * 80}")
    print("第三部分：不相关内容检查")
    print("=" * 80)
    
    irrelevant_found = []
    cur.execute("SELECT id, string_value FROM embedding_metadata WHERE key='chroma:document'")
    for row in cur.fetchall():
        content = row['string_value'] or ''
        rid = row['id']
        for kw in IRRELEVANT_KEYWORDS:
            if kw in content:
                idx_pos = content.find(kw)
                context = content[max(0,idx_pos-30):idx_pos+50].replace('\n', ' ')
                cur2 = conn.cursor()
                cur2.execute("SELECT string_value FROM embedding_metadata WHERE id=? AND key='filename'", (rid,))
                fn_row = cur2.fetchone()
                filename = fn_row[0] if fn_row else '未知'
                irrelevant_found.append((filename, kw, context))
    
    if irrelevant_found:
        print(f"\n⚠️ 发现 {len(irrelevant_found)} 处可能不相关的内容:")
        seen = set()
        for fn, kw, ctx in irrelevant_found:
            key = f"{fn}|{kw}"
            if key not in seen:
                seen.add(key)
                print(f"  文件: {fn}")
                print(f"  关键词: 【{kw}】")
                print(f"  上下文: ...{ctx}...")
                print()
    else:
        print("\n✅ 未发现不相关内容")

    # ========== 4. yam 文件夹对比 ==========
    print(f"\n{'=' * 80}")
    print("第四部分：yam 文件夹 vs 知识库 对比")
    print("=" * 80)
    
    yam_dir = r"d:\study\项目\国外包2\guowaibao_ys\backend\data\yam"
    yam_files = set(os.listdir(yam_dir)) if os.path.exists(yam_dir) else set()
    
    # 过滤掉非文件
    yam_files = {f for f in yam_files if os.path.isfile(os.path.join(yam_dir, f))}
    
    db_files = set(f['filename'] for f in files)
    
    in_yam_not_db = yam_files - db_files
    in_db_not_yam = db_files - yam_files
    
    print(f"\nyam 文件夹文件数: {len(yam_files)}")
    print(f"知识库文件记录数: {len(db_files)}")
    
    if in_yam_not_db:
        print(f"\n⚠️ yam 文件夹中存在但知识库中没有的文件 ({len(in_yam_not_db)} 个):")
        for f in sorted(in_yam_not_db):
            ext = os.path.splitext(f)[1].lower()
            print(f"  [{ext}] {f}")
    
    if in_db_not_yam:
        print(f"\n⚠️ 知识库中存在但 yam 文件夹中没有的文件 ({len(in_db_not_yam)} 个):")
        for f in sorted(in_db_not_yam):
            print(f"  {f}")
    
    if not in_yam_not_db and not in_db_not_yam:
        print("\n✅ yam 文件夹和知识库完全一致")

    # ========== 5. 空内容检查 ==========
    print(f"\n{'=' * 80}")
    print("第五部分：空内容/占位符检查")
    print("=" * 80)
    
    empty_or_placeholder = []
    cur.execute("SELECT id, string_value FROM embedding_metadata WHERE key='chroma:document'")
    for row in cur.fetchall():
        content = row['string_value'] or ''
        rid = row['id']
        if len(content.strip()) < 20 or 'extraction not yet implemented' in content or '无法识别' in content or 'tesseract is not installed' in content:
            cur2 = conn.cursor()
            cur2.execute("SELECT string_value FROM embedding_metadata WHERE id=? AND key='filename'", (rid,))
            fn_row = cur2.fetchone()
            filename = fn_row[0] if fn_row else '未知'
            empty_or_placeholder.append((filename, content[:100].replace('\n', '\\n')))
    
    if empty_or_placeholder:
        print(f"\n⚠️ 发现 {len(empty_or_placeholder)} 条空内容或占位符记录:")
        for fn, preview in empty_or_placeholder:
            print(f"  文件: {fn}")
            print(f"  内容: {preview}")
            print()
    else:
        print("\n✅ 所有记录都有有效内容")

    conn.close()
    os.remove(WORK_COPY)

if __name__ == "__main__":
    main()