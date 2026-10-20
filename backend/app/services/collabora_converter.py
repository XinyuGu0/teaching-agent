import os
import time
import tempfile
import httpx
from flask import current_app


def convert_ppt_to_pptx(source_path: str) -> str:
    """Convert ppt to pptx using Collabora Online conversion endpoint.

    Returns converted file path on success, otherwise None.
    """
    collabora_url = current_app.config.get('WOPI_BASE_URL')
    if not collabora_url:
        return None

    convert_url = collabora_url.rstrip('/') + '/lool/convert-to/pptx'
    if not os.path.exists(source_path):
        return None

    filename = os.path.basename(source_path)
    with open(source_path, 'rb') as f:
        files = {'file': (filename, f, 'application/vnd.ms-powerpoint')}
        try:
            response = httpx.post(convert_url, files=files, timeout=60)
            response.raise_for_status()
        except Exception:
            return None

    target_path = os.path.splitext(source_path)[0] + '.pptx'
    try:
        with open(target_path, 'wb') as out:
            out.write(response.content)
    except Exception:
        return None

    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        return target_path

    return None


def convert_pptx_to_pngs_via_powerpoint(source_path: str, output_dir: str) -> list:
    """Convert PPT/PPTX to per-slide PNG via local PowerPoint COM (Windows).

    This preserves embedded images/charts better than XML copy approaches.
    """
    if os.name != 'nt':
        return []
    if not os.path.exists(source_path):
        return []

    os.makedirs(output_dir, exist_ok=True)

    try:
        import pythoncom
        import win32com.client
    except Exception:
        return []

    exported = []
    app = None
    presentation = None
    try:
        pythoncom.CoInitialize()
        app = win32com.client.DispatchEx('PowerPoint.Application')
        app.Visible = 0
        presentation = app.Presentations.Open(source_path, WithWindow=False, ReadOnly=True)

        for idx in range(1, presentation.Slides.Count + 1):
            target_path = os.path.join(output_dir, f'slide_{idx}.png')
            presentation.Slides(idx).Export(target_path, 'PNG')
            if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                exported.append(target_path)
    except Exception:
        exported = []
    finally:
        try:
            if presentation is not None:
                presentation.Close()
        except Exception:
            pass
        try:
            if app is not None:
                app.Quit()
        except Exception:
            pass
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

    return exported


def _convert_pptx_to_pdf(source_path: str) -> str:
    """Convert pptx to pdf using Collabora convert endpoint.

    Returns PDF file path on success, otherwise None.
    """
    collabora_url = current_app.config.get('WOPI_BASE_URL')
    if not collabora_url or not os.path.exists(source_path):
        return None

    convert_url = collabora_url.rstrip('/') + '/lool/convert-to/pdf'
    filename = os.path.basename(source_path)

    with open(source_path, 'rb') as f:
        files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
        try:
            response = httpx.post(convert_url, files=files, timeout=120)
            response.raise_for_status()
        except Exception:
            return None

    try:
        fd, pdf_path = tempfile.mkstemp(prefix='pptx_slides_', suffix='.pdf')
        os.close(fd)
        with open(pdf_path, 'wb') as out:
            out.write(response.content)

        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            return pdf_path
    except Exception:
        return None

    return None


def _convert_pdf_to_pngs(pdf_path: str, output_dir: str) -> list:
    """Render PDF pages to PNG files via PyMuPDF."""
    if not pdf_path or not os.path.exists(pdf_path):
        return []

    try:
        import fitz
    except Exception:
        return []

    os.makedirs(output_dir, exist_ok=True)
    png_paths = []

    try:
        doc = fitz.open(pdf_path)
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            # 2x 缩放，保证清晰度
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            target_path = os.path.join(output_dir, f'slide_{page_index + 1}.png')
            pix.save(target_path)
            if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                png_paths.append(target_path)
        doc.close()
    except Exception:
        return []

    return png_paths


def convert_pptx_to_pngs_libreoffice(source_path: str, output_dir: str) -> list:
    """Convert pptx to png using LibreOffice command line (soffice).
    
    This method doesn't require Collabora service.
    """
    import subprocess
    
    if not os.path.exists(source_path):
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 使用 LibreOffice 导出为 PNG
        # --headless 无界面模式
        # --convert-to 输出格式
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'png',
            '--outdir', output_dir,
            source_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        if result.returncode != 0:
            print(f"[LibreOffice] Conversion failed: {result.stderr}")
            return []
        
        # 收集生成的 PNG 文件
        png_paths = []
        for f in os.listdir(output_dir):
            if f.lower().endswith('.png'):
                png_paths.append(os.path.join(output_dir, f))
        
        # 按文件名排序（slide_1.png, slide_2.png, etc.）
        def extract_page_num(path):
            import re
            match = re.search(r'slide[_\s]*(\d+)', os.path.basename(path), re.IGNORECASE)
            return int(match.group(1)) if match else 999999
        
        png_paths.sort(key=extract_page_num)
        return png_paths
        
    except Exception as e:
        print(f"[LibreOffice] Exception: {e}")
        return []


def convert_pptx_to_pngs(source_path: str, output_dir: str) -> list:
    """Convert pptx to png images.

    Priority:
    1) LibreOffice command line (independent of Collabora)
    2) Windows local PowerPoint COM export (best fidelity)
    3) Collabora convert-to/png
    4) Collabora convert-to/pdf + local PDF render per page
    """
    # 优先使用 LibreOffice 命令行（不依赖 Collabora 服务）
    png_paths = convert_pptx_to_pngs_libreoffice(source_path, output_dir)
    if png_paths:
        return png_paths
    
    # 优先使用本地PowerPoint导出，避免模板内图片丢失
    power_point_pngs = convert_pptx_to_pngs_via_powerpoint(source_path, output_dir)
    if power_point_pngs:
        return power_point_pngs

    collabora_url = current_app.config.get('WOPI_BASE_URL')
    if not collabora_url:
        return []

    convert_url = collabora_url.rstrip('/') + '/lool/convert-to/png'
    if not os.path.exists(source_path):
        return []

    os.makedirs(output_dir, exist_ok=True)

    # 先尝试整体转换
    png_paths = []
    filename = os.path.basename(source_path)
    with open(source_path, 'rb') as f:
        files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
        try:
            response = httpx.post(convert_url, files=files, timeout=120)
            response.raise_for_status()
        except Exception:
            response = None

    if response is not None:
        content_type = response.headers.get('Content-Type', '')
        content_disp = response.headers.get('Content-Disposition', '')

        if 'application/zip' in content_type:
            import zipfile
            import io
            try:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                    for name in zf.namelist():
                        if name.lower().endswith('.png'):
                            target_path = os.path.join(output_dir, os.path.basename(name))
                            with open(target_path, 'wb') as out:
                                out.write(zf.read(name))
                            if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                                png_paths.append(target_path)
            except Exception:
                png_paths = []
        elif 'image/png' in content_type or ('.png"' in content_disp.lower()):
            target_path = os.path.join(output_dir, 'slide_1.png')
            try:
                with open(target_path, 'wb') as out:
                    out.write(response.content)
                if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                    png_paths.append(target_path)
            except Exception:
                png_paths = []

    # 兜底：如果只导出了1页或没有导出，改用 PDF 按页渲染，保证多页模板可见
    if len(png_paths) <= 1:
        pdf_path = _convert_pptx_to_pdf(source_path)
        if pdf_path:
            try:
                pdf_pngs = _convert_pdf_to_pngs(pdf_path, output_dir)
                if len(pdf_pngs) > len(png_paths):
                    png_paths = pdf_pngs
            finally:
                try:
                    os.remove(pdf_path)
                except Exception:
                    pass

    return png_paths
