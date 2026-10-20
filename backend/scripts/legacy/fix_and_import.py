"""
1. 删除数据库基础知识.pdf中的广告内容
2. 导入yam文件夹中未入库的14个文件（纯SQLite操作）
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
import sys
import re
import shutil
import sqlite3
import uuid
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REAL_VECTOR_DB = r"d:\study\项目\国外包2\guowaibao_ys\backend\data\vector_db"
WORK_COPY = r"C:\Users\yejia\rag_work\fix_work.sqlite3"
YAM_DIR = r"d:\study\项目\国外包2\guowaibao_ys\backend\data\yam"

def extract_text_from_htm(fp):
    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            with open(fp, 'r', encoding=enc) as f:
                c = f.read()
            break
        except:
            continue
    else:
        return ""
    c = re.sub(r'<script[^>]*>.*?</script>', '', c, flags=re.DOTALL)
    c = re.sub(r'<style[^>]*>.*?</style>', '', c, flags=re.DOTALL)
    c = re.sub(r'<[^>]+>', ' ', c)
    c = re.sub(r'\s+', ' ', c).strip()
    return c

def extract_text_from_ppt_via_libreoffice(fp):
    """用LibreOffice转换.ppt为.pptx再提取"""
    soffice = None
    for p in [r'C:\Program Files\LibreOffice\program\soffice.exe',
              r'C:\Program Files (x86)\LibreOffice\program\soffice.exe']:
        if os.path.exists(p):
            soffice = p
            break
    if not soffice:
        import subprocess
        soffice = shutil.which('soffice')
    
    if not soffice:
        return None, "LibreOffice not found"
    
    import subprocess, tempfile
    td = tempfile.mkdtemp(prefix='ppt_conv_')
    try:
        subprocess.run([soffice, '--headless', '--convert-to', 'pptx', '--outdir', td, fp],
                      capture_output=True, timeout=120)
        pptx_file = None
        for f in os.listdir(td):
            if f.endswith('.pptx'):
                pptx_file = os.path.join(td, f)
                break
        if not pptx_file:
            return None, "Conversion failed"
        
        from pptx import Presentation
        prs = Presentation(pptx_file)
        tc = [f"[总页数]: {len(prs.slides)}"]
        for sn, slide in enumerate(prs.slides, 1):
            si = [f"\n[幻灯片 {sn}/{len(prs.slides)}]"]
            ts = [s.text for s in slide.shapes if hasattr(s, "text") and s.text.strip()]
            if ts:
                si.append(f"【标题】: {ts[0]}")
                if len(ts) > 1:
                    si.append("【内容】:")
                    for i, t in enumerate(ts[1:], 1):
                        si.append(f"  {i}. {t}")
            tc.append("\n".join(si))
        text = "\n".join(tc)
        shutil.rmtree(td)
        return text, None
    except Exception as e:
        if os.path.exists(td):
            shutil.rmtree(td)
        return None, str(e)

def chunk_text(text, size=2000, overlap=200):
    if not text or len(text.strip()) < 10:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if end < len(text):
            for sep in ['。', '！', '？', '.', '\n\n', '；']:
                idx = chunk.rfind(sep)
                if idx > size * 0.5:
                    chunk = chunk[:idx+1]
                    end = start + idx + 1
                    break
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 10]

def main():
    print("=" * 60)
    print("修复广告 + 导入未入库文件")
    print("=" * 60)

    src_db = os.path.join(REAL_VECTOR_DB, "chroma.sqlite3")
    if os.path.exists(WORK_COPY):
        os.remove(WORK_COPY)
    shutil.copy2(src_db, WORK_COPY)

    conn = sqlite3.connect(WORK_COPY)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # ========== 1. 删除广告 ==========
    print("\n📢 步骤1: 清理广告内容")
    
    # 获取数据库基础知识.pdf id=210 的内容
    cur.execute("SELECT string_value FROM embedding_metadata WHERE id=210 AND key='chroma:document'")
    row = cur.fetchone()
    if row:
        old_content = row[0]
        # 删除广告部分
        ad_text = "卧槽，还有10T 计算机和运营资料、以及各种红包和实物抽奖！同时加入程序员交流群，绝对没有广告只有交流和学习，毫无套路！详情：https://t.1yb.co/3WEl 也可以加我微信：tsdabear 快速入群！"
        new_content = old_content.replace(ad_text, "")
        # 清理多余空白
        new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content).strip()
        
        cur.execute("UPDATE embedding_metadata SET string_value=? WHERE id=210 AND key='chroma:document'", (new_content,))
        print(f"  ✅ 广告已删除 (id=210, 内容从 {len(old_content)} → {len(new_content)} 字符)")
        
        # 更新FTS
        try:
            cur.execute("UPDATE embedding_fulltext_search SET string_value=? WHERE rowid=210", (new_content,))
            print(f"  ✅ FTS 已更新")
        except Exception as e:
            print(f"  ⚠️ FTS: {e}")
    else:
        print("  ⚠️ 未找到 id=210 的记录")

    # ========== 2. 导入未入库文件 ==========
    print("\n📁 步骤2: 导入未入库文件")
    
    # 未入库文件列表
    unimported = [
        ("2第二讲关系代数.ppt", "ppt"),
        ("index..htm", "html"),
        ("jxdy1.htm", "html"),
        ("jxdy2.htm", "html"),
        ("jxdy3.htm", "html"),
        ("jxdy4.htm", "html"),
        ("jxdy5.htm", "html"),
        ("jxdy6.htm", "html"),
        ("jxdy7.htm", "html"),
        ("jxdy8.htm", "html"),
        ("kczy.htm", "html"),
        ("kczyfe.htm", "html"),
        ("kczyxx.htm", "html"),
        ("wps1.png", "image"),
    ]
    
    # 获取 segment_id（从已有记录中取）
    cur.execute("SELECT DISTINCT segment_id FROM embeddings LIMIT 1")
    seg_row = cur.fetchone()
    segment_id = seg_row[0] if seg_row else None
    print(f"  使用 segment_id: {segment_id}")
    
    # 获取最大 id
    cur.execute("SELECT MAX(id) FROM embeddings")
    max_id = cur.fetchone()[0] or 0
    print(f"  当前最大 id: {max_id}")
    
    # 获取最大 seq_id
    cur.execute("SELECT MAX(seq_id) FROM embeddings")
    max_seq_row = cur.fetchone()
    
    user_id = "a727de8f-c791-47e1-908a-9ae7002b550f"
    total_added = 0
    
    for idx, (filename, file_type) in enumerate(unimported):
        fp = os.path.join(YAM_DIR, filename)
        if not os.path.exists(fp):
            print(f"\n  [{idx+1}] ⚠️ 文件不存在: {filename}")
            continue
        
        print(f"\n  [{idx+1}/{len(unimported)}] {filename} ({file_type})")
        
        text = None
        if file_type == "html":
            text = extract_text_from_htm(fp)
        elif file_type == "ppt":
            text, err = extract_text_from_ppt_via_libreoffice(fp)
            if err:
                print(f"    ⚠️ PPT提取失败: {err}")
                continue
        elif file_type == "image":
            print(f"    ⏭️ 图片文件，跳过（需要LLM描述后手动入库）")
            continue
        
        if not text or len(text.strip()) < 10:
            print(f"    ⚠️ 内容太少 ({len(text) if text else 0} 字符)")
            continue
        
        print(f"    ✅ 提取: {len(text)} 字符")
        
        chunks = chunk_text(text)
        if not chunks:
            print(f"    ⚠️ 分块为空")
            continue
        print(f"    ✅ 分块: {len(chunks)} 块")
        
        doc_uuid = str(uuid.uuid4())
        
        for ci, chunk in enumerate(chunks):
            max_id += 1
            embedding_id = f"{doc_uuid}_chunk_{ci}"
            
            # 插入 embeddings 记录
            seq_id = max_id  # 简单使用 id 作为 seq_id
            cur.execute(
                "INSERT INTO embeddings (id, segment_id, embedding_id, seq_id) VALUES (?, ?, ?, ?)",
                (max_id, segment_id, embedding_id, seq_id)
            )
            
            # 插入 metadata
            metas = [
                (max_id, 'chroma:document', chunk),
                (max_id, 'document_id', doc_uuid),
                (max_id, 'user_id', user_id),
                (max_id, 'filename', filename),
                (max_id, 'file_type', file_type),
                (max_id, 'chunk_index', str(ci)),
                (max_id, 'total_chunks', str(len(chunks))),
            ]
            for mid, key, val in metas:
                cur.execute("INSERT INTO embedding_metadata (id, key, string_value) VALUES (?, ?, ?)", (mid, key, val))
            
            # 插入 FTS
            try:
                cur.execute("INSERT INTO embedding_fulltext_search (rowid, string_value) VALUES (?, ?)", (max_id, chunk))
            except Exception as e:
                print(f"    ⚠️ FTS插入失败: {e}")
            
            total_added += 1
        
        print(f"    ✅ 已存入 {len(chunks)} 条")
    
    # 检查结果
    cur.execute("SELECT COUNT(*) FROM embeddings")
    total = cur.fetchone()[0]
    print(f"\n📊 更新后总记录数: {total}")

    conn.commit()
    conn.close()
    
    # 复制回原路径
    shutil.copy2(WORK_COPY, src_db)
    print(f"✅ 数据库已复制回原路径")
    
    os.remove(WORK_COPY)
    print(f"✅ 临时文件已清理")
    
    print(f"\n{'=' * 60}")
    print(f"操作完成！")
    print(f"  - 广告: 已清理")
    print(f"  - 新增: {total_added} 条记录")
    print(f"  - wps1.png: 需要LLM描述后手动入库")
    print(f"  ⚠️ 新记录无向量（HNSW崩溃），仅支持文本搜索")

if __name__ == "__main__":
    main()