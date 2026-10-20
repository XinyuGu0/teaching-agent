"""
内置PPT模板脚本 - 根据build.sh内容模板化生成PPT
每个模板保留风格命令（颜色、位置、形状、装饰），文字内容替换为用户大纲
通过subprocess调用officecli命令（Windows兼容）

核心策略：
1. 读取原始模板的 .pptx 文件作为基础
2. 使用 officecli set 命令替换命名文本元素的内容
3. 保留所有装饰元素、颜色、位置、动画不变
"""
import os
import json
import subprocess
import logging
import tempfile
import shutil
import time

logger = logging.getLogger(__name__)


def _run_cmd(cmd, timeout=60):
    """执行officecli命令"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            shell=(os.name == 'nt'), encoding='utf-8', errors='replace'
        )
        if result.returncode != 0:
            logger.warning(f"[BuiltinTemplate] cmd failed: {' '.join(cmd)}, stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        logger.error(f"[BuiltinTemplate] cmd error: {e}")
        return False


def _get_slide_shapes(file_path, slide_num):
    """获取指定slide中所有shape的信息"""
    try:
        result = subprocess.run(
            ['officecli', 'query', file_path, f'/slide[{slide_num}]', '--json'],
            capture_output=True, text=True, timeout=30,
            shell=(os.name == 'nt'), encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            # officecli 返回 {"success": true, "data": {"Matches": N, "Results": [...]}}
            if isinstance(data, dict) and 'data' in data:
                results = data['data'].get('Results', [])
            elif isinstance(data, list):
                results = data
            else:
                results = []
            logger.info(f"[BuiltinTemplate] Slide {slide_num} 共有 {len(results)} 个shapes")
            return results
        else:
            logger.warning(f"[BuiltinTemplate] query failed for slide {slide_num}: {result.stderr}")
            return []
    except Exception as e:
        logger.error(f"[BuiltinTemplate] query error: {e}")
        return []


def _find_shape_index(shapes, target_names):
    """
    通用shape查找：在shapes列表中按关键词模糊匹配
    target_names: 可能的名称关键词列表，按优先级排序
    shape名称在 format.name 字段中，格式为 "!!hero-title" 等
    匹配策略：去掉!!前缀后，检查target是否包含在shape名称中（双向包含）
    返回: (index, name) 或 (None, None)
    """
    if not shapes:
        return None, None
    
    for target_name in target_names:
        target_lower = target_name.lower()
        for i, shape in enumerate(shapes, start=1):
            # shape名称在 format.name 中，也可能在 preview 中
            fmt = shape.get('format', {})
            shape_name = ''
            if isinstance(fmt, dict):
                shape_name = fmt.get('name', '')
            if not shape_name:
                shape_name = shape.get('preview', '')
            if not shape_name:
                continue
            
            # 去掉 !! 前缀
            clean_name = shape_name.lstrip('!').lower()
            
            # 精确匹配
            if target_lower == clean_name:
                logger.info(f"[BuiltinTemplate] 精确匹配: index={i}, name={shape_name}")
                return i, shape_name
            
            # 双向包含匹配
            if target_lower in clean_name or clean_name in target_lower:
                logger.info(f"[BuiltinTemplate] 模糊匹配: index={i}, name={shape_name}, target={target_name}")
                return i, shape_name
    
    logger.warning(f"[BuiltinTemplate] 未找到匹配的shape: targets={target_names}")
    return None, None


def _run_batch(file_path, batch_data):
    """执行officecli batch命令"""
    tmp_file_path = None
    try:
        # 清理数据中的所有控制字符
        clean_data = _clean_for_json(batch_data)
        
        # 创建临时文件路径
        tmp_file_path = os.path.join(tempfile.gettempdir(), f'officecli_batch_{os.getpid()}_{int(time.time())}.json')
        
        # 写入JSON - 使用 'wb' 模式直接写入字节，避免任何编码转换问题
        json_bytes = json.dumps(clean_data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        
        with open(tmp_file_path, 'wb') as f:
            f.write(json_bytes)
        
        # 调试：打印生成的JSON
        logger.info(f"[BuiltinTemplate] Batch JSON file: {tmp_file_path}")
        logger.info(f"[BuiltinTemplate] Batch JSON size: {len(json_bytes)} bytes")
        logger.info(f"[BuiltinTemplate] Batch JSON content: {json_bytes[:500].decode('utf-8', errors='replace')}...")
        
        # 使用文件路径作为参数，而不是stdin
        result = subprocess.run(
            ['officecli', 'batch', file_path, '--input', tmp_file_path],
            capture_output=True, text=True, timeout=180,
            shell=(os.name == 'nt'), encoding='utf-8', errors='replace'
        )
        
        if result.returncode != 0:
            logger.warning(f"[BuiltinTemplate] batch failed: {result.stderr}")
            logger.warning(f"[BuiltinTemplate] batch stdout: {result.stdout}")
        else:
            logger.info(f"[BuiltinTemplate] batch success: {result.stdout}")
        return result.returncode == 0
    except Exception as e:
        logger.error(f"[BuiltinTemplate] batch error: {e}")
        import traceback
        logger.error(f"[BuiltinTemplate] traceback: {traceback.format_exc()}")
        return False
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except:
                pass


def _extract_outline_data(outline):
    """从大纲数据中提取各页内容，映射到5页结构"""
    logger.info(f"[BuiltinTemplate] ========== _extract_outline_data 开始 ==========")
    logger.info(f"[BuiltinTemplate] 输入 outline 类型: {type(outline)}")
    logger.info(f"[BuiltinTemplate] 输入 outline 内容: {json.dumps(outline, ensure_ascii=False, indent=2)[:2000]}")
    
    slides = outline.get('slides', [])
    logger.info(f"[BuiltinTemplate] slides 数量: {len(slides)}")
    
    # 提取主题标题
    title = outline.get('title', '')
    if not title and slides:
        first_slide = slides[0] if slides else {}
        title = first_slide.get('title', '演示文稿')
    
    logger.info(f"[BuiltinTemplate] 提取的主题标题: {title}")
    
    data = {
        'title': title,
        'slides': []
    }
    
    # 将用户大纲映射到5页结构：hero, statement, pillars, evidence, cta
    for i, slide in enumerate(slides[:5]):
        slide_data = {
            'title': slide.get('title', f'第{i+1}页'),
            'points': slide.get('content_points', slide.get('points', [])),
            'notes': slide.get('notes', ''),
        }
        logger.info(f"[BuiltinTemplate] Slide {i+1}: title='{slide_data['title']}', points={slide_data['points'][:2] if slide_data['points'] else []}")
        data['slides'].append(slide_data)
    
    # 如果不足5页，用默认内容填充
    while len(data['slides']) < 5:
        idx = len(data['slides'])
        logger.info(f"[BuiltinTemplate] 填充默认 Slide {idx+1}")
        data['slides'].append({
            'title': f'第{idx+1}部分',
            'points': ['内容要点'],
            'notes': ''
        })
    
    logger.info(f"[BuiltinTemplate] 最终提取数据: {json.dumps(data, ensure_ascii=False, indent=2)[:1500]}")
    logger.info(f"[BuiltinTemplate] ========== _extract_outline_data 完成 ==========")
    
    return data


# ============================================================
# 模板风格数据 - 从各build.sh提取的颜色/布局参数
# ============================================================

TEMPLATES = {
    'science--alien-guide': {
        'colors': {'BG': '0B0C10', 'ACCENT1': '66FCF1', 'ACCENT2': '45A29E', 'WHITE': 'FFFFFF', 'GRAY': 'C5C6C7', 'DARK': '1F2833'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'science--time-travel': {
        'colors': {'BG': '050510', 'ACCENT1': '00FFFF', 'ACCENT2': '8A2BE2', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '111122'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'science--space-exploration': {
        'colors': {'BG': '050510', 'ACCENT1': '00BFFF', 'ACCENT2': '1A1A3E', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '0A0A2E'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'science--mars-settlement': {
        'colors': {'BG': '080A1F', 'ACCENT1': 'FF5722', 'ACCENT2': '2196F3', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '1A0A0A'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'brand--aura-coffee': {
        'colors': {'BG': 'F9F6F0', 'ACCENT1': '2B2624', 'ACCENT2': 'C2A878', 'WHITE': 'FFFFFF', 'GRAY': '8B6F47', 'DARK': 'F3EFE6'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'brand--aura-coffee-dark': {
        'colors': {'BG': '1A1612', 'ACCENT1': 'C2A878', 'ACCENT2': '8B6F47', 'WHITE': 'F5F0E8', 'GRAY': 'A89880', 'DARK': '2B2624'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'product--aionui-promo': {
        'colors': {'BG': '0A0A1A', 'ACCENT1': '6C63FF', 'ACCENT2': '00D4AA', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '151530'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'product--geminicli-timetravel': {
        'colors': {'BG': '0A0A1A', 'ACCENT1': '4285F4', 'ACCENT2': '34A853', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '151530'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'lifestyle--cat-philosophy': {
        'colors': {'BG': 'FFF8F0', 'ACCENT1': 'FF8C42', 'ACCENT2': 'FFD166', 'WHITE': 'FFFFFF', 'GRAY': '666666', 'DARK': '2D2D2D'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'lifestyle--cat-secret-life': {
        'colors': {'BG': 'FDF6EC', 'ACCENT1': 'E07A5F', 'ACCENT2': '81B29A', 'WHITE': 'FFFFFF', 'GRAY': '777777', 'DARK': '3D405B'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'lifestyle--feline-report': {
        'colors': {'BG': '1E1E1E', 'ACCENT1': 'FFD700', 'ACCENT2': 'FF004D', 'WHITE': 'FFFFFF', 'GRAY': 'CCCCCC', 'DARK': '2A2A2A'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'productivity--attention-budget': {
        'colors': {'BG': '0B0F1A', 'ACCENT1': '2BE4A8', 'ACCENT2': 'FFB020', 'WHITE': 'FFFFFF', 'GRAY': 'B9C6D6', 'DARK': '5B6CFF'},
        'font': 'PingFang SC',
        'slide_count': 5,
    },
    'tech--wildlife-company': {
        'colors': {'BG': '0F1923', 'ACCENT1': '4CAF50', 'ACCENT2': 'FF9800', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '1A2A3A'},
        'font': '思源黑体',
        'slide_count': 5,
    },
    'future--2050-vision': {
        'colors': {'BG': '0A0A2E', 'ACCENT1': '00E5FF', 'ACCENT2': 'FF6B35', 'WHITE': 'FFFFFF', 'GRAY': 'AAAAAA', 'DARK': '151540'},
        'font': '思源黑体',
        'slide_count': 5,
    },
}


def _escape_text(text):
    """清理文本内容，移除所有可能导致JSON问题的控制字符"""
    if not text:
        return ""
    text = str(text)
    
    # officecli 的 JSON 解析器非常严格，不允许任何未转义的控制字符
    # 必须移除所有控制字符（0x00-0x1F 和 0x7F）
    import re
    # 移除所有控制字符，包括换行、回车、制表符等
    # 使用空格替换，保持文本连贯性
    text = re.sub(r'[\x00-\x1f\x7f]', ' ', text)
    # 合并多个连续空格为单个空格
    text = re.sub(r' +', ' ', text)
    return text.strip()


def _clean_for_json(data):
    """递归清理数据结构中的所有字符串，移除控制字符"""
    if isinstance(data, str):
        return _escape_text(data)
    elif isinstance(data, dict):
        return {k: _clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_clean_for_json(item) for item in data]
    else:
        return data


def _build_ppt_from_template(file_path, template_id, outline_data, progress_callback=None):
    """
    从模板构建PPT - 复制原始pptx，然后用officecli替换文字
    
    策略：
    1. 复制模板的原始 .pptx 文件
    2. 查询每个slide中的所有shape，找到对应的索引
    3. 使用 officecli set 命令（数字索引）替换文本内容
    4. 保持所有样式、动画、装饰不变
    """
    logger.info(f"[BuiltinTemplate] ========== _build_ppt_from_template 开始 ==========")
    logger.info(f"[BuiltinTemplate] template_id: {template_id}")
    logger.info(f"[BuiltinTemplate] file_path: {file_path}")
    logger.info(f"[BuiltinTemplate] outline_data: {json.dumps(outline_data, ensure_ascii=False, indent=2)[:2000]}")
    
    template_info = TEMPLATES.get(template_id)
    if not template_info:
        logger.error(f"[BuiltinTemplate] 未知模板: {template_id}")
        return {'success': False, 'error': f'未知模板: {template_id}'}
    
    # 找到原始pptx文件路径
    styles_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..',
        'OfficeCLI-main', 'examples', 'ppt', 'templates', 'styles'
    ))
    template_dir = os.path.join(styles_dir, template_id)
    
    if not os.path.isdir(template_dir):
        return {'success': False, 'error': f'模板目录不存在: {template_dir}'}
    
    # 查找pptx文件
    pptx_file = None
    for f in os.listdir(template_dir):
        if f.endswith('.pptx') and not f.startswith('~'):
            pptx_file = f
            break
    
    if not pptx_file:
        return {'success': False, 'error': f'模板目录中无pptx文件: {template_dir}'}
    
    src_path = os.path.join(template_dir, pptx_file)
    if not os.path.exists(src_path):
        return {'success': False, 'error': f'模板文件不存在: {src_path}'}
    
    # 复制模板文件到输出路径
    shutil.copy2(src_path, file_path)
    logger.info(f"[BuiltinTemplate] 已复制模板文件: {src_path} -> {file_path}")
    
    slides = outline_data.get('slides', [])
    title = outline_data.get('title', '演示文稿')
    
    logger.info(f"[BuiltinTemplate] 大纲标题: {title}")
    logger.info(f"[BuiltinTemplate] slides 数量: {len(slides)}")
    
    if not slides:
        logger.warning(f"[BuiltinTemplate] 无大纲数据，使用原始模板")
        return {'success': True, 'file_path': file_path, 'message': '使用原始模板（无大纲数据）'}
    
    # 构建文本替换命令 - 通用策略
    replacements = []
    
    # 查询每个slide的shapes
    slide_shapes_cache = {}
    for slide_num in range(1, 6):
        shapes = _get_slide_shapes(file_path, slide_num)
        slide_shapes_cache[slide_num] = shapes
        logger.info(f"[BuiltinTemplate] Slide {slide_num} 共有 {len(shapes)} 个shapes")
    
    # 通用替换策略：对每个slide，遍历所有有文本的shape，按名称关键词自动匹配
    for slide_num in range(1, 6):
        if slide_num > len(slides):
            break
        
        slide_data = slides[slide_num - 1]
        slide_title = _escape_text(slide_data.get('title', ''))
        slide_points = slide_data.get('points', [])
        shapes = slide_shapes_cache.get(slide_num, [])
        
        # 收集该slide中所有有文本的shape（排除背景装饰）
        text_shapes = []
        for i, s in enumerate(shapes, 1):
            fmt = s.get('format', {})
            name = fmt.get('name', '') if isinstance(fmt, dict) else ''
            text = s.get('text', '')
            if not name.startswith('!!') or not text:
                continue
            # 排除背景/装饰shape（bg, glow, star, ring, line, dot, circle, slash, card, deco, orbit, planet等）
            clean = name.lstrip('!').lower()
            if any(kw in clean for kw in ['bg-', 'glow', 'star-', 'ring', 'line-', 'dot-', 'circle', 'slash', 'card-', 'deco', 'orbit', 'planet', 'line-top', 'line-accent']):
                continue
            text_shapes.append((i, name, clean, text))
        
        if not text_shapes:
            continue
        
        logger.info(f"[BuiltinTemplate] Slide {slide_num}: {len(text_shapes)} text shapes to process")
        
        # 对每个有文本的shape，根据名称关键词决定替换内容
        for idx, name, clean, orig_text in text_shapes:
            new_text = None
            
            # === 标题类 ===
            if any(kw in clean for kw in ['hero-title', 'brand-title']):
                # 只在slide 1替换hero-title
                if slide_num == 1:
                    new_text = slide_title or title
                # 其他slide的hero-title是背景装饰，也替换为总标题
                else:
                    new_text = title
            
            elif any(kw in clean for kw in ['hero-sub', 'hero-subtitle', 'brand-sub']):
                if slide_num == 1:
                    new_text = _escape_text(' | '.join(slide_points[:2])) if slide_points else ''
                else:
                    new_text = _escape_text(' | '.join(slide_points[:2])) if slide_points else ''
            
            # === Statement 类 ===
            elif any(kw in clean for kw in ['statement-text', 'statement-main', 'statement-title']):
                new_text = slide_title
            
            elif any(kw in clean for kw in ['statement-sub', 'statement-subtitle', 'statement-desc']):
                new_text = _escape_text(' '.join(slide_points[:3]))
            
            # === Pillar 类 ===
            elif 'pillar-title' in clean or 'pillars-title' in clean:
                new_text = slide_title
            
            elif any(f'pillar-{n}' in clean for n in ['1', '2', '3']):
                # 提取pillar编号
                for n in ['1', '2', '3']:
                    if f'pillar-{n}' in clean:
                        point_idx = int(n) - 1
                        if point_idx < len(slide_points):
                            if 'title' in clean:
                                new_text = _escape_text(slide_points[point_idx])
                            elif 'desc' in clean:
                                new_text = _escape_text(slide_points[point_idx])
                            elif 'num' in clean:
                                new_text = str(point_idx + 1)  # 序号
                            else:
                                new_text = _escape_text(slide_points[point_idx])
                        break
            
            elif any(f'p{n}' in clean for n in ['1', '2', '3']):
                for n in ['1', '2', '3']:
                    if f'p{n}-' in clean or clean == f'p{n}':
                        point_idx = int(n) - 1
                        if point_idx < len(slide_points):
                            new_text = _escape_text(slide_points[point_idx])
                        break
            
            elif any(f'box{n}' in clean for n in ['1', '2', '3']):
                for n in ['1', '2', '3']:
                    if f'box{n}' in clean:
                        point_idx = int(n) - 1
                        if point_idx < len(slide_points):
                            new_text = _escape_text(slide_points[point_idx])
                        break
            
            # === Evidence / Showcase 类 ===
            elif any(kw in clean for kw in ['evi-title', 'ev-title', 'evidence-title', 'showcase-title']):
                new_text = slide_title
            
            elif any(kw in clean for kw in ['evi-data', 'evi-desc', 'ev-desc', 'evidence-main', 'evidence-point']):
                new_text = _escape_text(' '.join(slide_points[:3]))
            
            elif any(kw in clean for kw in ['showcase-quote', 'showcase-subtitle']):
                new_text = _escape_text(slide_points[0]) if slide_points else ''
            
            elif any(kw in clean for kw in ['showcase-data', 'evi-num', 'evi-t']):
                # 数据展示shape，用对应的point
                for n in ['1', '2', '3']:
                    if n in clean:
                        point_idx = int(n) - 1
                        if point_idx < len(slide_points):
                            new_text = _escape_text(slide_points[point_idx])
                        break
                if not new_text and slide_points:
                    new_text = _escape_text(' '.join(slide_points[:3]))
            
            # === CTA 类 ===
            elif any(kw in clean for kw in ['cta-title', 'quote-main']):
                new_text = slide_title
            
            elif any(kw in clean for kw in ['cta-sub', 'cta-text', 'cta-web', 'cta-email', 'cta-subtitle']):
                new_text = _escape_text(' '.join(slide_points[:2]))
            
            if new_text:
                replacements.append({"command": "set", "path": f"/slide[{slide_num}]/shape[{idx}]", "props": {"text": new_text}})
                logger.info(f"[BuiltinTemplate]   Slide {slide_num} [{idx}] {name}: '{new_text[:50]}'")
    
    logger.info(f"[BuiltinTemplate] 总共构建了 {len(replacements)} 个替换命令")
    
    # 执行替换
    if replacements:
        logger.info(f"[BuiltinTemplate] 开始执行 batch 命令...")
        if progress_callback:
            progress_callback({'progress': 50, 'message': '正在替换文本内容...'})
        
        success = _run_batch(file_path, replacements)
        if not success:
            logger.warning(f"[BuiltinTemplate] 部分文本替换可能失败")
    
    return {'success': True, 'file_path': file_path}


def generate_builtin_ppt(template_id: str, output_path: str, outline: dict, progress_callback=None) -> dict:
    """
    统一入口：根据内置模板ID生成PPT
    
    Args:
        template_id: 内置模板ID（如 'builtin_science--time-travel'）
        output_path: 输出文件路径
        outline: 大纲数据
        progress_callback: 进度回调
    
    Returns:
        {'success': bool, 'file_path': str, 'error': str}
    """
    logger.info(f"[BuiltinTemplate] ========== generate_builtin_ppt 开始 ==========")
    logger.info(f"[BuiltinTemplate] template_id: {template_id}")
    logger.info(f"[BuiltinTemplate] output_path: {output_path}")
    logger.info(f"[BuiltinTemplate] outline 类型: {type(outline)}")
    logger.info(f"[BuiltinTemplate] outline 内容: {json.dumps(outline, ensure_ascii=False, indent=2)[:3000]}")
    
    # 提取dir_name
    if template_id.startswith('builtin_'):
        dir_name = template_id[8:]
    else:
        dir_name = template_id
    
    logger.info(f"[BuiltinTemplate] dir_name: {dir_name}")
    
    if dir_name not in TEMPLATES:
        logger.error(f"[BuiltinTemplate] 未知内置模板: {dir_name}")
        return {'success': False, 'error': f'未知内置模板: {template_id}'}
    
    outline_data = _extract_outline_data(outline)
    logger.info(f"[BuiltinTemplate] 提取后 outline_data: {json.dumps(outline_data, ensure_ascii=False, indent=2)[:2000]}")
    
    if progress_callback:
        progress_callback({'progress': 10, 'message': f'使用内置模板 {dir_name} 生成PPT...'})
    
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    if progress_callback:
        progress_callback({'progress': 30, 'message': '复制模板文件...'})
    
    result = _build_ppt_from_template(output_path, dir_name, outline_data, progress_callback)
    
    if progress_callback:
        progress_callback({'progress': 90, 'message': '模板应用完成...'})
    
    return result
