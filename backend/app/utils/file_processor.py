"""
File processor for extracting text from various document formats
"""
import os
import shutil
import subprocess
import tempfile
from typing import Optional

def _convert_legacy_office(file_path: str, target_ext: str) -> Optional[str]:
    """
    使用 LibreOffice 将旧版 Office 文件 (.ppt, .doc, .xls) 转换为现代格式 (.pptx, .docx, .xlsx)。
    返回转换后文件的路径，失败则返回 None。
    """
    # 检测 LibreOffice/soffice 是否可用
    soffice = shutil.which('soffice') or shutil.which('libreoffice')
    if not soffice:
        # Windows 下常见路径
        win_paths = [
            r'C:\Program Files\LibreOffice\program\soffice.exe',
            r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        ]
        for p in win_paths:
            if os.path.exists(p):
                soffice = p
                break
    if not soffice:
        print(f"[WARN] LibreOffice not found, cannot convert {file_path}")
        return None

    try:
        tmp_dir = tempfile.mkdtemp(prefix='office_convert_')
        cmd = [
            soffice,
            '--headless',
            '--convert-to', target_ext,
            '--outdir', tmp_dir,
            file_path,
        ]
        print(f"[DEBUG] Converting {file_path} -> {target_ext} using LibreOffice")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"[WARN] LibreOffice conversion failed: {result.stderr}")
            return None

        # 找到输出文件
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        converted_path = os.path.join(tmp_dir, base_name + '.' + target_ext)
        if os.path.exists(converted_path):
            print(f"[DEBUG] Conversion succeeded: {converted_path}")
            return converted_path

        # 如果文件名有变化，查找目录下所有匹配扩展名的文件
        for f in os.listdir(tmp_dir):
            if f.endswith('.' + target_ext):
                converted_path = os.path.join(tmp_dir, f)
                print(f"[DEBUG] Conversion succeeded (alt): {converted_path}")
                return converted_path

        print(f"[WARN] LibreOffice output file not found in {tmp_dir}")
        return None
    except Exception as e:
        print(f"[WARN] LibreOffice conversion error: {e}")
        return None


def extract_text(file_path: str, file_type: str) -> str:
    """
    Extract text from document based on file type

    Args:
        file_path: Path to the file
        file_type: Type of file (pdf, word, ppt, excel, image, video)

    Returns:
        Extracted text content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    extractors = {
        'pdf': extract_from_pdf,
        'word': extract_from_word,
        'ppt': extract_from_ppt,
        'excel': extract_from_excel,
        'image': extract_from_image,
        'video': extract_from_video,
        'text': extract_from_text,
        'audio': extract_from_audio,
    }

    extractor = extractors.get(file_type)
    if not extractor:
        raise ValueError(f"Unsupported file type: {file_type}")

    return extractor(file_path)


def extract_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        import fitz  # PyMuPDF

        text_content = []
        doc = fitz.open(file_path)

        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                text_content.append(f"[Page {page_num}]\n{text}")

        doc.close()
        return "\n\n".join(text_content)

    except Exception as e:
        raise Exception(f"Error extracting PDF: {str(e)}")


def extract_from_word(file_path: str) -> str:
    """Extract text from Word document with enhanced formatting (supports .doc and .docx)"""
    actual_path = file_path

    # 如果是旧版 .doc 格式，尝试转换为 .docx
    if file_path.lower().endswith('.doc') and not file_path.lower().endswith('.docx'):
        converted_path = _convert_legacy_office(file_path, 'docx')
        if converted_path:
            actual_path = converted_path
        else:
            return f"[Word文件]: {os.path.basename(file_path)}\n[提示]: 旧版 .doc 格式无法直接提取文本，建议转换为 .docx 后重新上传"

    try:
        from docx import Document

        doc = Document(actual_path)
        text_content = []
        
        # 添加文档标题和样式信息
        text_content.append(f"[文档标题]: {doc.core_properties.title or '未命名文档'}")
        text_content.append(f"[作者]: {doc.core_properties.author or '未知'}")
        text_content.append(f"[文档类型]: Word文档")
        text_content.append("")

        # Extract paragraphs with style information
        for para in doc.paragraphs:
            if para.text.strip():
                style_name = para.style.name if para.style else "Normal"
                # 标题样式
                if 'Heading' in style_name or 'Title' in style_name:
                    text_content.append(f"\n【{para.text}】")
                else:
                    text_content.append(para.text)

        # Extract text from tables
        table_count = 0
        for table in doc.tables:
            table_count += 1
            text_content.append(f"\n\n[表格 {table_count}]")
            for row_idx, row in enumerate(table.rows):
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_content.append(" | ".join(row_text))

        if table_count > 0:
            text_content.append(f"\n\n[共 {table_count} 个表格]")

        return "\n".join(text_content)

    except Exception as e:
        raise Exception(f"Error extracting Word: {str(e)}")


def extract_from_ppt(file_path: str) -> str:
    """Extract text from PowerPoint with enhanced structure (supports .ppt and .pptx)"""
    actual_path = file_path
    converted_path = None

    # 如果是旧版 .ppt 格式，尝试转换为 .pptx
    if file_path.lower().endswith('.ppt') and not file_path.lower().endswith('.pptx'):
        converted_path = _convert_legacy_office(file_path, 'pptx')
        if converted_path:
            actual_path = converted_path
        else:
            # 转换失败，降级：标记为已上传但无法提取文本
            return f"[PPT文件]: {os.path.basename(file_path)}\n[提示]: 旧版 .ppt 格式无法直接提取文本，建议转换为 .pptx 后重新上传"

    try:
        from pptx import Presentation

        prs = Presentation(actual_path)
        text_content = []
        
        # 添加演示文稿信息
        text_content.append(f"[演示文稿类型]: PowerPoint演示")
        text_content.append(f"[总页数]: {len(prs.slides)}")
        text_content.append("")

        for slide_num, slide in enumerate(prs.slides, 1):
            slide_info = []
            slide_info.append(f"\n[幻灯片 {slide_num}/{len(prs.slides)}]")
            
            # 提取所有文本
            text_shapes = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text_shapes.append(shape.text)
            
            if text_shapes:
                # 幻灯片标题通常是第一个文本框
                if len(text_shapes) > 0:
                    slide_info.append(f"\n【标题】: {text_shapes[0]}")
                
                # 其他内容
                if len(text_shapes) > 1:
                    slide_info.append("\n【内容】:")
                    for i, text in enumerate(text_shapes[1:], 1):
                        slide_info.append(f"  {i}. {text}")
                
                # 检查是否有表格
                tables = [shape for shape in slide.shapes if shape.has_table]
                if tables:
                    slide_info.append(f"\n[包含 {len(tables)} 个表格]")
            
            text_content.append("\n".join(slide_info))

        return "\n".join(text_content)

    except Exception as e:
        raise Exception(f"Error extracting PPT: {str(e)}")


def extract_from_excel(file_path: str) -> str:
    """Extract text from Excel (supports .xls and .xlsx)"""
    actual_path = file_path

    # 如果是旧版 .xls 格式，尝试转换为 .xlsx
    if file_path.lower().endswith('.xls') and not file_path.lower().endswith('.xlsx'):
        converted_path = _convert_legacy_office(file_path, 'xlsx')
        if converted_path:
            actual_path = converted_path
        else:
            return f"[Excel文件]: {os.path.basename(file_path)}\n[提示]: 旧版 .xls 格式无法直接提取文本，建议转换为 .xlsx 后重新上传"

    try:
        import pandas as pd

        # Read all sheets
        excel_file = pd.ExcelFile(actual_path)
        text_content = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(actual_path, sheet_name=sheet_name)

            # Convert dataframe to text
            sheet_text = [f"[Sheet: {sheet_name}]"]

            # Add column headers
            headers = " | ".join(str(col) for col in df.columns)
            sheet_text.append(headers)

            # Add rows (limit to first 100 rows to avoid too much data)
            for idx, row in df.head(100).iterrows():
                row_text = " | ".join(str(val) for val in row.values if pd.notna(val))
                if row_text.strip():
                    sheet_text.append(row_text)

            text_content.append("\n".join(sheet_text))

        return "\n\n".join(text_content)

    except Exception as e:
        raise Exception(f"Error extracting Excel: {str(e)}")


def extract_from_image(file_path: str) -> str:
    """Extract and understand image content using GLM-4V"""
    try:
        import base64
        from app.services import glm_service
        
        # 读取图片并转为base64
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 获取图片格式
        from PIL import Image
        img = Image.open(file_path)
        img_format = img.format.lower()
        if img_format not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            img_format = 'png'  # 默认使用png
        
        # 构建图片URL
        image_url = f"data:image/{img_format};base64,{image_data}"
        
        # 使用GLM-4V分析图片
        prompt = """请详细分析这张图片，包括：
1. 图片中的文字内容（如果有）
2. 图片的主要内容和主题
3. 图片的风格和特征
4. 图片中的关键元素
5. 图片的整体描述

请用中文回答，尽可能详细和准确。"""
        
        try:
            # 调用GLM-4V视觉模型
            response = glm_service.analyze_image(
                image_url=image_url,
                prompt=prompt
            )
            
            if response and len(response.strip()) > 10:
                # 添加图片信息前缀
                result = f"[图片类型]: {img_format.upper()}图片\n"
                result += f"[图片尺寸]: {img.size[0]}x{img.size[1]}\n"
                result += f"[AI分析内容]:\n{response}"
                return result
            else:
                # 如果AI分析失败，尝试OCR
                import pytesseract
                text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                if text.strip():
                    result = f"[图片类型]: {img_format.upper()}图片\n"
                    result += f"[OCR识别文字]:\n{text.strip()}"
                    return result
                else:
                    return f"[图片类型]: {img_format.upper()}图片\n[图片描述]: 图片内容无法识别"
                    
        except Exception as ai_error:
            print(f"[DEBUG] GLM-4V分析失败，尝试OCR: {ai_error}")
            # 降级到OCR
            import pytesseract
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            if text.strip():
                result = f"[图片类型]: {img_format.upper()}图片\n"
                result += f"[OCR识别文字]:\n{text.strip()}"
                return result
            else:
                return f"[图片类型]: {img_format.upper()}图片\n[图片描述]: 图片内容无法识别"

    except Exception as e:
        print(f"[ERROR] 图片处理失败: {e}")
        return f"[图片文件]: {os.path.basename(file_path)}\n[错误]: {str(e)}"


def extract_from_video(file_path: str) -> str:
    """Extract keyframes from video (placeholder)"""
    # Video processing is complex and resource-intensive
    # For now, just return a placeholder
    # In production, you might extract keyframes and use GLM-4V
    return f"[Video file: {os.path.basename(file_path)} - Video content extraction not yet implemented]"


def extract_from_text(file_path: str) -> str:
    """Extract text from plain text or markdown files"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return f"[Text file: {os.path.basename(file_path)} - Unable to decode file content]"


def extract_from_audio(file_path: str) -> str:
    """Extract metadata from audio files (placeholder for ASR)"""
    return f"[Audio file: {os.path.basename(file_path)} - Audio transcription not yet implemented]"
