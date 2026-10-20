"""
将 yam 文件夹中的文件导入 RAG 知识库
使用英文临时路径解决 ChromaDB 中文路径崩溃问题
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
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import uuid
import re

YAM_DIR = r"d:\study\项目\国外包2\guowaibao_ys\backend\data\yam"
REAL_VECTOR_DB = r"d:\study\项目\国外包2\guowaibao_ys\backend\data\vector_db"
TEMP_VECTOR_DB = r"C:\Users\yejia\rag_work\vector_db"

FILE_TYPE_MAP = {
    '.pdf': 'pdf', '.doc': 'word', '.docx': 'word',
    '.ppt': 'ppt', '.pptx': 'ppt',
    '.xls': 'excel', '.xlsx': 'excel',
    '.txt': 'text', '.md': 'text',
    '.htm': 'html', '.html': 'html',
    '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
    '.mp4': 'video', '.avi': 'video', '.mov': 'video',
    '.mp3': 'audio', '.wav': 'audio',
}
SKIP_TYPES = {'image', 'video', 'audio'}

def extract_from_pdf(fp):
    import fitz
    texts, doc = [], fitz.open(fp)
    for pn, p in enumerate(doc, 1):
        t = p.get_text()
        if t.strip(): texts.append(f"[第{pn}页]\n{t}")
    doc.close()
    return "\n\n".join(texts)

def extract_from_word(fp):
    actual = fp
    if fp.lower().endswith('.doc') and not fp.lower().endswith('.docx'):
        import subprocess, tempfile
        soffice = shutil.which('soffice')
        if not soffice:
            for p in [r'C:\Program Files\LibreOffice\program\soffice.exe',
                       r'C:\Program Files (x86)\LibreOffice\program\soffice.exe']:
                if os.path.exists(p): soffice = p; break
        if soffice:
            td = tempfile.mkdtemp(prefix='conv_')
            subprocess.run([soffice, '--headless', '--convert-to', 'docx', '--outdir', td, fp],
                         capture_output=True, timeout=120)
            for f in os.listdir(td):
                if f.endswith('.docx'): actual = os.path.join(td, f); break
    from docx import Document
    doc = Document(actual)
    tc = []
    if doc.core_properties.title: tc.append(f"[文档标题]: {doc.core_properties.title}")
    for para in doc.paragraphs:
        if para.text.strip():
            sn = para.style.name if para.style else ""
            tc.append(f"\n【{para.text}】" if 'Heading' in sn or 'Title' in sn else para.text)
    for i, tbl in enumerate(doc.tables, 1):
        tc.append(f"\n[表格 {i}]")
        for row in tbl.rows:
            rt = [c.text.strip() for c in row.cells if c.text.strip()]
            if rt: tc.append(" | ".join(rt))
    return "\n".join(tc)

def extract_from_ppt(fp):
    actual = fp
    if fp.lower().endswith('.ppt') and not fp.lower().endswith('.pptx'):
        import subprocess, tempfile
        soffice = shutil.which('soffice')
        if not soffice:
            for p in [r'C:\Program Files\LibreOffice\program\soffice.exe',
                       r'C:\Program Files (x86)\LibreOffice\program\soffice.exe']:
                if os.path.exists(p): soffice = p; break
        if soffice:
            td = tempfile.mkdtemp(prefix='conv_')
            subprocess.run([soffice, '--headless', '--convert-to', 'pptx', '--outdir', td, fp],
                         capture_output=True, timeout=120)
            for f in os.listdir(td):
                if f.endswith('.pptx'): actual = os.path.join(td, f); break
    from pptx import Presentation
    prs = Presentation(actual)
    tc = [f"[总页数]: {len(prs.slides)}"]
    for sn, slide in enumerate(prs.slides, 1):
        si = [f"\n[幻灯片 {sn}/{len(prs.slides)}]"]
        ts = [s.text for s in slide.shapes if hasattr(s, "text") and s.text.strip()]
        if ts:
            si.append(f"【标题】: {ts[0]}")
            if len(ts) > 1:
                si.append("【内容】:")
                for i, t in enumerate(ts[1:], 1): si.append(f"  {i}. {t}")
        tc.append("\n".join(si))
    return "\n".join(tc)

def extract_from_text(fp):
    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            with open(fp, 'r', encoding=enc) as f: return f.read()
        except: continue
    return ""

def extract_from_html(fp):
    c = extract_from_text(fp)
    c = re.sub(r'<script[^>]*>.*?</script>', '', c, flags=re.DOTALL)
    c = re.sub(r'<style[^>]*>.*?</style>', '', c, flags=re.DOTALL)
    c = re.sub(r'<[^>]+>', ' ', c)
    return re.sub(r'\s+', ' ', c).strip()

EXTRACTORS = {'pdf': extract_from_pdf, 'word': extract_from_word, 'ppt': extract_from_ppt,
              'text': extract_from_text, 'html': extract_from_html}

def chunk_text(text, size=2000, overlap=200):
    if not text or len(text.strip()) < 10: return []
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if end < len(text):
            for sep in ['。', '！', '？', '.', '\n\n', '；']:
                idx = chunk.rfind(sep)
                if idx > size * 0.5:
                    chunk = chunk[:idx+1]; end = start + idx + 1; break
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 10]

def generate_embeddings(texts, batch_size=20):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["EMBEDDING_API_KEY"],
                    base_url="https://open.bigmodel.cn/api/paas/v4")
    all_emb = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"    Embedding 批次 {i//batch_size+1}/{(len(texts)-1)//batch_size+1}")
        try:
            resp = client.embeddings.create(model="embedding-3", input=batch)
            all_emb.extend([item.embedding for item in resp.data])
        except Exception as e:
            print(f"    ⚠ 失败: {e}")
            all_emb.extend([[0.0]*1024 for _ in batch])
        time.sleep(0.5)
    return all_emb

def main():
    print("=" * 60)
    print("RAG 知识库导入工具 - yam 文件夹")
    print("=" * 60)
    
    # 1. 复制 vector_db 到英文临时路径
    if os.path.exists(TEMP_VECTOR_DB):
        shutil.rmtree(TEMP_VECTOR_DB)
    shutil.copytree(REAL_VECTOR_DB, TEMP_VECTOR_DB)
    print(f"✅ 已复制 vector_db 到临时路径: {TEMP_VECTOR_DB}")
    
    # 2. 删除旧的 HNSW 索引文件（让 ChromaDB 重建）
    for dirpath, dirnames, filenames in os.walk(TEMP_VECTOR_DB):
        for fn in filenames:
            if fn.endswith('.bin'):
                fp = os.path.join(dirpath, fn)
                os.remove(fp)
                print(f"  清理索引: {fp}")
    
    # 3. 直接用 chromadb 连接临时路径（不用 Flask）
    import chromadb
    from chromadb.config import Settings
    
    client = chromadb.PersistentClient(
        path=TEMP_VECTOR_DB,
        settings=Settings(anonymized_telemetry=False, allow_reset=True)
    )
    collection = client.get_or_create_collection(
        name="documents",
        metadata={"description": "Document chunks for RAG"}
    )
    
    existing_count = collection.count()
    print(f"当前知识库记录数: {existing_count}")
    
    # 获取已有文件名
    existing = collection.get(include=["metadatas"])
    existing_files = set(m.get('filename', '') for m in existing['metadatas'])
    print(f"已有文件: {len(existing_files)} 个")
    
    # 4. 扫描 yam 文件夹
    to_process, to_skip, to_exist = [], [], []
    for fn in sorted(os.listdir(YAM_DIR)):
        fp = os.path.join(YAM_DIR, fn)
        if not os.path.isfile(fp): continue
        ext = os.path.splitext(fn)[1].lower()
        ft = FILE_TYPE_MAP.get(ext, 'other')
        if ft in SKIP_TYPES: to_skip.append((fn, ft))
        elif fn in existing_files: to_exist.append(fn)
        elif ft == 'other': to_skip.append((fn, 'unknown'))
        else: to_process.append((fn, fp, ft))
    
    print(f"\n--- 文件分析 ---")
    print(f"可处理: {len(to_process)} | 已存在: {len(to_exist)} | 需辅助: {len(to_skip)}")
    
    if to_skip:
        print(f"\n🔶 需要大模型辅助的文件:")
        for f, ft in to_skip: print(f"  [{ft}] {f}")
    
    if to_exist:
        print(f"\n⏭ 已存在跳过:")
        for f in to_exist: print(f"  {f}")
    
    if not to_process:
        print("\n无新文件需要处理")
        shutil.rmtree(TEMP_VECTOR_DB)
        return
    
    # 5. 处理文件
    user_id = "a727de8f-c791-47e1-908a-9ae7002b550f"
    total_added = 0
    
    for idx, (fn, fp, ft) in enumerate(to_process):
        print(f"\n[{idx+1}/{len(to_process)}] {fn} ({ft})")
        
        extractor = EXTRACTORS.get(ft)
        if not extractor:
            print(f"  ⚠ 无提取器"); continue
        
        try:
            text = extractor(fp)
        except Exception as e:
            print(f"  ❌ 提取失败: {e}"); continue
        
        if not text or len(text.strip()) < 10:
            print(f"  ⚠ 内容太少 ({len(text)}字符)"); continue
        print(f"  ✅ 提取: {len(text)} 字符")
        
        chunks = chunk_text(text)
        if not chunks:
            print(f"  ⚠ 分块为空"); continue
        print(f"  ✅ 分块: {len(chunks)} 块")
        
        try:
            embeddings = generate_embeddings(chunks)
        except Exception as e:
            print(f"  ❌ Embedding 失败: {e}"); continue
        print(f"  ✅ Embedding 完成")
        
        doc_uuid = str(uuid.uuid4())
        chunk_ids = [f"yam_{doc_uuid}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                'document_id': doc_uuid,
                'user_id': user_id,
                'filename': fn,
                'file_type': ft,
                'chunk_index': str(i),
                'total_chunks': str(len(chunks)),
            }
            for i in range(len(chunks))
        ]
        
        try:
            collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )
            total_added += len(chunks)
            print(f"  ✅ 已存入 {len(chunks)} 条")
        except Exception as e:
            print(f"  ❌ 存储失败: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"导入完成！新增 {total_added} 条向量记录")
    print(f"知识库总记录数: {collection.count()}")
    
    # 6. 复制回原路径
    print(f"\n正在将更新后的数据库复制回原路径...")
    # 删除旧路径的索引文件
    for dirpath, dirnames, filenames in os.walk(REAL_VECTOR_DB):
        for fn in filenames:
            if fn.endswith('.bin'):
                os.remove(os.path.join(dirpath, fn))
    
    # 复制所有文件
    for dirpath, dirnames, filenames in os.walk(TEMP_VECTOR_DB):
        reldir = os.path.relpath(dirpath, TEMP_VECTOR_DB)
        dstdir = os.path.join(REAL_VECTOR_DB, reldir)
        os.makedirs(dstdir, exist_ok=True)
        for fn in filenames:
            src = os.path.join(dirpath, fn)
            dst = os.path.join(dstdir, fn)
            shutil.copy2(src, dst)
    
    print(f"✅ 数据库已复制回原路径")
    
    # 清理
    shutil.rmtree(TEMP_VECTOR_DB)
    print(f"✅ 临时文件已清理")

if __name__ == "__main__":
    main()