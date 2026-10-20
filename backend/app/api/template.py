from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.template import Template
import os
import uuid
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename
from PIL import Image
from app.services.collabora_converter import convert_ppt_to_pptx, convert_pptx_to_pngs

bp = Blueprint('template', __name__)
bp.strict_slashes = False

# 显式处理OPTIONS请求，避免Flask重定向
@bp.route('/<path:path>', methods=['OPTIONS'])
@bp.route('/<path:path>/', methods=['OPTIONS'])
@bp.route('/', methods=['OPTIONS'])
def handle_template_options(path=None):
    """处理所有OPTIONS预检请求"""
    return '', 204

# 允许的PPT文件扩展名
ALLOWED_PPT_EXTENSIONS = {'pptx', 'ppt'}
# 允许的图片扩展名（用于缩略图）
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 模板分类
TEMPLATE_CATEGORIES = {
    'business': '商务',
    'education': '教育',
    'creative': '创意',
    'minimal': '极简',
    'technology': '科技',
    'medical': '医疗',
    'finance': '金融',
    'art': '艺术',
    'other': '其他'
}


def allowed_ppt_file(filename):
    """检查文件是否是PPT格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_PPT_EXTENSIONS


def allowed_image_file(filename):
    """检查文件是否是图片格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def parse_template_styles(ppt_path):
    """解析PPT模板样式"""
    try:
        from app.services.template_parser import TemplateParser
        styles = TemplateParser.parse_template(ppt_path)
        return styles
    except Exception as e:
        print(f"[TEMPLATE] TemplateParser 解析失败: {e}")
        
        # 尝试使用视觉模型分析
        try:
            print(f"[TEMPLATE] 尝试使用视觉模型分析...")
            from app.services.vision_service import vision_service
            
            vision_result = vision_service.analyze_ppt_layout(ppt_path, max_pages=2)
            
            if vision_result.get('success'):
                print(f"[TEMPLATE] ✓ 视觉模型分析成功")
                
                # 转换视觉模型的结果为标准格式
                styles = {
                    'slide_layouts': [],
                    'colors': vision_result.get('styles', {}).get('colors', {}),
                    'fonts': vision_result.get('styles', {}).get('fonts', {}),
                    'backgrounds': []
                }
                
                # 转换页面布局信息
                for page in vision_result.get('pages', []):
                    layout_info = {
                        'slide_number': page.get('page_number', 0) - 1,
                        'layout_type': page.get('layout_type', 'unknown'),
                        'elements': [],
                        'summary': page.get('elements', {})
                    }
                    
                    # 转换文本框
                    for box in page.get('text_boxes', []):
                        element = {
                            'type': 'text',
                            'text': '',
                            'position': {
                                'x': 0, 'y': 0, 'w': 0, 'h': 0
                            },
                            'font': {
                                'name': box.get('font_name', 'Arial'),
                                'size': box.get('font_size', 18),
                                'bold': box.get('font_bold', False),
                                'color': page.get('color_scheme', {}).get('secondary', '000000')
                            }
                        }
                        layout_info['elements'].append(element)
                    
                    styles['slide_layouts'].append(layout_info)
                
                print(f"[TEMPLATE]   - 页数: {vision_result.get('analyzed_pages', 0)}")
                print(f"[TEMPLATE]   - 颜色: {styles.get('colors', {})}")
                print(f"[TEMPLATE]   - 字体: {styles.get('fonts', {})}")
                
                return styles
            
        except Exception as e2:
            print(f"[TEMPLATE] 视觉模型分析失败: {e2}")
            import traceback
            traceback.print_exc()
        
        # 如果视觉模型失败，尝试使用 _generate_slide_from_template
        try:
            print(f"[TEMPLATE] 尝试直接提取模板布局...")
            from app.services.structured_ppt_generator import StructuredPPTGenerator
            
            generator = StructuredPPTGenerator()
            
            # 提取前2页的布局
            sample_slides_data = []
            for i in range(min(2, generator._get_template_slide_count(ppt_path))):
                slide_data = generator._generate_slide_from_template(
                    ppt_path,
                    slide_index=i,
                    title="测试标题",
                    content=["测试内容"],
                    is_title=(i == 0)
                )
                sample_slides_data.append(slide_data)
            
            # 从提取的布局中构建样式信息
            if sample_slides_data:
                styles = {
                    'slide_layouts': [
                        {
                            'slide_number': i,
                            'layout_type': 'title' if i == 0 else 'content',
                            'elements': slide.get('objects', []),
                            'summary': {
                                'text_elements': len([obj for obj in slide.get('objects', []) if obj.get('type') == 'text']),
                                'image_elements': len([obj for obj in slide.get('objects', []) if obj.get('type') == 'image']),
                                'shape_elements': len(slide.get('objects', [])) - len([obj for obj in slide.get('objects', []) if obj.get('type') in ['text', 'image']])
                            }
                        }
                        for i, slide in enumerate(sample_slides_data)
                    ],
                    'colors': {},
                    'fonts': {},
                    'backgrounds': []
                }
                
                # 提取背景色
                for slide in sample_slides_data:
                    bg = slide.get('background', {})
                    if 'color' in bg:
                        slide_type = 'title_slide' if slide.get('slide_number') == 1 else 'content_slide'
                        if slide_type not in styles['colors']:
                            styles['colors'][slide_type] = {}
                        styles['colors'][slide_type]['primary'] = bg['color']
                
                # 提取字体
                for slide in sample_slides_data:
                    for obj in slide.get('objects', []):
                        if obj.get('type') == 'text':
                            opts = obj.get('options', {})
                            font_name = opts.get('font', 'Arial')
                            font_size = opts.get('fontSize', 18)
                            bold = opts.get('bold', False)
                            
                            # 判断是标题还是正文
                            if font_size > 24 or bold:
                                if 'name' not in styles['fonts'].get('title', {}):
                                    if 'title' not in styles['fonts']:
                                        styles['fonts']['title'] = {}
                                    styles['fonts']['title']['name'] = font_name
                                    styles['fonts']['title']['size'] = font_size
                                    styles['fonts']['title']['bold'] = bold
                            else:
                                if 'name' not in styles['fonts'].get('body', {}):
                                    if 'body' not in styles['fonts']:
                                        styles['fonts']['body'] = {}
                                    styles['fonts']['body']['name'] = font_name
                                    styles['fonts']['body']['size'] = font_size
                
                print(f"[TEMPLATE] ✓ 成功提取模板样式:")
                print(f"[TEMPLATE]   - 页数: {len(sample_slides_data)}")
                print(f"[TEMPLATE]   - 颜色: {styles.get('colors', {})}")
                print(f"[TEMPLATE]   - 字体: {styles.get('fonts', {})}")
                
                return styles
            
        except Exception as e3:
            print(f"[TEMPLATE] 直接提取布局也失败: {e3}")
            import traceback
            traceback.print_exc()
        
        # 返回默认样式
        from app.services.template_parser import TemplateParser
        default_styles = TemplateParser._get_default_styles()
        print(f"[TEMPLATE] 使用默认样式")
        return default_styles


def create_default_thumbnail(thumbnail_path):
    """创建默认缩略图"""
    img = Image.new('RGB', (800, 600), color='#f0f0f0')
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
        draw.text((400, 300), "PPT模板", fill='#333333', font=font, anchor='mm')
    except Exception:
        pass
    img.save(thumbnail_path)
    return True


def extract_template_slide_images(ppt_path, template_id):
    """将模板每页转换为图片，返回图片文件路径列表"""
    slides_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'templates',
        'slides',
        str(template_id)
    )
    os.makedirs(slides_dir, exist_ok=True)

    png_paths = convert_pptx_to_pngs(ppt_path, slides_dir)

    def _slide_index(path):
        base = os.path.basename(path)
        try:
            # slide_1.png / Slide1.png 等情况
            import re
            match = re.search(r'(?:slide[_\s-]?)(\d+)', base, re.IGNORECASE)
            return int(match.group(1)) if match else 999999
        except Exception:
            return 999999

    png_paths = sorted([p for p in png_paths if os.path.exists(p)], key=_slide_index)
    return png_paths


@bp.route('/', methods=['OPTIONS'])
def handle_options():
    """处理OPTIONS预检请求，避免重定向"""
    return '', 204


@bp.route('/builtin', methods=['GET'])
@bp.route('/builtin/', methods=['GET'])
@jwt_required()
def get_builtin_templates():
    """获取内置模板列表（硬编码数据，不查数据库）"""
    try:
        from app.services.builtin_templates import get_all_builtin_templates, get_builtin_categories
        
        templates = get_all_builtin_templates()
        categories = get_builtin_categories()

        # 为内置模板补充封面URL（用于模板管理/聊天选择弹窗展示）
        public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
        if not public_base_url:
            public_base_url = request.host_url.rstrip('/')

        normalized_templates = []
        for item in templates:
            t = dict(item)
            tid = str(t.get('id') or '')
            if tid:
                t['thumbnail_url'] = f"{public_base_url}/api/templates/builtin/{tid}/cover"
            normalized_templates.append(t)
        
        return jsonify({
            'templates': normalized_templates,
            'categories': {k: v['label'] for k, v in categories.items()}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/builtin/<template_id>', methods=['GET'])
@jwt_required()
def get_builtin_template_detail(template_id):
    """获取单个内置模板详情"""
    try:
        from app.services.builtin_templates import get_builtin_template
        
        template = get_builtin_template(template_id)
        if not template:
            return jsonify({'error': '内置模板不存在'}), 404
        
        return jsonify(template), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _resolve_builtin_template_cover_path(template_id: str):
    """返回内置模板封面绝对路径；不存在则返回None。"""
    normalized = str(template_id or '')
    if not normalized:
        return None
    if not normalized.startswith('builtin_'):
        normalized = f'builtin_{normalized}'

    dir_name = normalized.replace('builtin_', '', 1)
    cover_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'templates',
        'builtin',
        'covers'
    )
    # 支持多种图片后缀
    exts = ['png', 'jpg', 'jpeg', 'gif']
    for ext in exts:
        p = os.path.join(cover_dir, f'{dir_name}.{ext}')
        if os.path.exists(p):
            return p
    return None


def _resolve_builtin_template_ppt_path(template_id: str):
    """返回内置模板PPT文件绝对路径；不存在则返回None。"""
    normalized = str(template_id or '')
    if not normalized:
        return None
    if not normalized.startswith('builtin_'):
        normalized = f'builtin_{normalized}'

    dir_name = normalized.replace('builtin_', '', 1)
    style_dir = os.path.abspath(os.path.join(
        current_app.root_path,
        '..', '..',
        'OfficeCLI-main',
        'examples', 'ppt', 'templates', 'styles',
        dir_name
    ))
    if not os.path.isdir(style_dir):
        return None

    for ext in ['.pptx', '.ppt']:
        for filename in os.listdir(style_dir):
            if filename.lower().endswith(ext):
                full_path = os.path.join(style_dir, filename)
                if os.path.isfile(full_path):
                    return full_path
    return None


@bp.route('/builtin/<template_id>/cover', methods=['GET'])
@bp.route('/builtin/<template_id>/cover/', methods=['GET'])
def get_builtin_template_cover(template_id):
    """获取内置模板封面图"""
    try:
        cover_path = _resolve_builtin_template_cover_path(template_id)
        if not cover_path:
            return jsonify({'error': '内置模板封面不存在'}), 404
        return send_file(cover_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/builtin/<template_id>/cover', methods=['POST'])
@bp.route('/builtin/<template_id>/cover/', methods=['POST'])
@jwt_required()
def upload_builtin_template_cover(template_id):
    """上传内置模板封面图（模板管理使用）"""
    try:
        from app.services.builtin_templates import get_builtin_template

        normalized = str(template_id or '')
        if not normalized.startswith('builtin_'):
            normalized = f'builtin_{normalized}'

        builtin_template = get_builtin_template(normalized)
        if not builtin_template:
            return jsonify({'error': '内置模板不存在'}), 404

        if 'cover' not in request.files:
            return jsonify({'error': '请上传封面图片'}), 400

        cover_file = request.files['cover']
        if not cover_file or cover_file.filename == '':
            return jsonify({'error': '请选择封面图片'}), 400

        if not allowed_image_file(cover_file.filename):
            return jsonify({'error': '只支持PNG、JPG、JPEG、GIF格式的图片'}), 400

        ext = cover_file.filename.rsplit('.', 1)[1].lower()
        dir_name = normalized.replace('builtin_', '', 1)

        cover_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'templates',
            'builtin',
            'covers'
        )
        os.makedirs(cover_dir, exist_ok=True)

        # 同名覆盖，保证每个内置模板只有一张当前封面
        for old_ext in ['png', 'jpg', 'jpeg', 'gif']:
            old_path = os.path.join(cover_dir, f'{dir_name}.{old_ext}')
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass

        save_path = os.path.join(cover_dir, f'{dir_name}.{ext}')
        cover_file.save(save_path)

        public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
        if not public_base_url:
            public_base_url = request.host_url.rstrip('/')

        return jsonify({
            'message': '内置模板封面上传成功',
            'template_id': normalized,
            'thumbnail_url': f"{public_base_url}/api/templates/builtin/{normalized}/cover"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ppt-file/<path:filename>', methods=['GET'])
def get_ppt_file(filename):
    """提供 backend/ppt/ 目录下的PPT文件（供OnlyOffice访问）"""
    try:
        ppt_dir = os.path.join(current_app.config.get('BASE_DIR', os.path.abspath(os.path.join(current_app.root_path, '..'))), 'ppt')
        file_path = os.path.join(ppt_dir, filename)
        if not os.path.isfile(file_path):
            return jsonify({'error': '文件不存在'}), 404
        return send_file(file_path, as_attachment=False, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ppt-file/<path:filename>/preview', methods=['GET'])
@bp.route('/ppt-file/<path:filename>/preview/', methods=['GET'])
@jwt_required()
def get_ppt_file_preview(filename):
    """获取 backend/ppt/ 目录下PPT文件的预览配置（OnlyOffice 只读预览）"""
    try:
        user_id = get_jwt_identity()

        ppt_dir = os.path.join(current_app.config.get('BASE_DIR', os.path.abspath(os.path.join(current_app.root_path, '..'))), 'ppt')
        file_path = os.path.join(ppt_dir, filename)
        if not os.path.isfile(file_path):
            return jsonify({'error': '文件不存在'}), 404

        onlyoffice_url = current_app.config.get('ONLYOFFICE_URL', 'http://localhost:80')
        jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')

        public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
        if not public_base_url:
            public_base_url = request.host_url.rstrip('/')
        # OnlyOffice在Docker中无法解析localhost，替换为127.0.0.1
        public_base_url = public_base_url.replace('localhost', '127.0.0.1')

        file_url = f"{public_base_url}/api/templates/ppt-file/{filename}"

        import hashlib
        stat = os.stat(file_path)
        key_base = f"pptfile_{filename}_{stat.st_mtime}_{stat.st_size}"
        doc_key = hashlib.md5(key_base.encode()).hexdigest()

        doc_config = {
            'fileType': 'pptx',
            'key': doc_key,
            'title': filename,
            'url': file_url,
            'permissions': {
                'edit': False,
                'download': True,
                'print': True
            }
        }

        editor_cfg = {
            'lang': 'zh-CN',
            'mode': 'view',
            'user': {
                'id': str(user_id),
                'name': 'User'
            }
        }

        token = ''
        if jwt_secret:
            import jwt as pyjwt
            import time

            payload = {
                'document': doc_config,
                'documentType': 'presentation',
                'editorConfig': editor_cfg,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600
            }

            try:
                token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
            except Exception:
                token = ''

        return jsonify({
            'file_id': f'pptfile_{filename}',
            'file_name': filename,
            'file_url': file_url,
            'key': doc_key,
            'onlyoffice_url': onlyoffice_url,
            'token': token,
            'document': doc_config,
            'editor_config': editor_cfg,
            'access_token': token,
            'access_token_ttl': 3600
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/builtin/<template_id>/file', methods=['GET'])
@bp.route('/builtin/<template_id>/file/', methods=['GET'])
def get_builtin_template_file(template_id):
    """获取内置模板文件（供OnlyOffice访问）"""
    try:
        file_path = _resolve_builtin_template_ppt_path(template_id)
        if not file_path:
            return jsonify({'error': '内置模板文件不存在'}), 404
        return send_file(file_path, as_attachment=False, download_name=os.path.basename(file_path))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/builtin/<template_id>/preview', methods=['GET'])
@bp.route('/builtin/<template_id>/preview/', methods=['GET'])
@jwt_required()
def get_builtin_template_preview(template_id):
    """获取内置模板预览配置（OnlyOffice 只读预览）"""
    try:
        user_id = get_jwt_identity()

        normalized = str(template_id or '')
        if not normalized.startswith('builtin_'):
            normalized = f'builtin_{normalized}'

        from app.services.builtin_templates import get_builtin_template
        builtin_template = get_builtin_template(normalized)
        if not builtin_template:
            return jsonify({'error': '内置模板不存在'}), 404

        file_path = _resolve_builtin_template_ppt_path(normalized)
        if not file_path:
            return jsonify({'error': '内置模板文件不存在'}), 404

        file_name = os.path.basename(file_path)

        # OnlyOffice配置
        onlyoffice_url = current_app.config.get('ONLYOFFICE_URL', 'http://localhost:80')
        jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')

        # 生成文件访问URL
        public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
        if not public_base_url:
            public_base_url = request.host_url.rstrip('/')

        file_url = f"{public_base_url}/api/templates/builtin/{normalized}/file"

        # 生成文档key
        import hashlib
        stat = os.stat(file_path)
        key_base = f"{normalized}_{stat.st_mtime}_{stat.st_size}"
        doc_key = hashlib.md5(key_base.encode()).hexdigest()

        doc_config = {
            'fileType': 'pptx',
            'key': doc_key,
            'title': file_name,
            'url': file_url,
            'permissions': {
                'edit': False,
                'download': True,
                'print': True
            }
        }

        editor_cfg = {
            'lang': 'zh-CN',
            'mode': 'view',
            'user': {
                'id': str(user_id),
                'name': 'User'
            }
        }

        token = ''
        if jwt_secret:
            import jwt as pyjwt
            import time

            payload = {
                'document': doc_config,
                'documentType': 'presentation',
                'editorConfig': editor_cfg,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600
            }

            try:
                token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
            except Exception:
                token = ''

        return jsonify({
            'file_id': normalized,
            'file_name': file_name,
            'file_url': file_url,
            'key': doc_key,
            'onlyoffice_url': onlyoffice_url,
            'token': token,
            'document': doc_config,
            'editor_config': editor_cfg,
            'access_token': token,
            'access_token_ttl': 3600
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/analyze-save', methods=['POST'])
@bp.route('/analyze-save/', methods=['POST'])
@jwt_required()
def save_analyzed_template():
    """保存自定义分析模板（关联到内置PPT文件）"""
    try:
        user_id = get_jwt_identity()

        name = request.form.get('name', '自定义模板')
        description = request.form.get('description', '通过自动识别上传的自定义模板')
        category = request.form.get('category', 'other')
        preview_file = request.form.get('preview_file', '极简商务计划书.pptx')
        page_count = int(request.form.get('page_count', 8))
        placeholder_count = int(request.form.get('placeholder_count', 18))

        if category not in TEMPLATE_CATEGORIES:
            category = 'other'

        # 验证关联的PPT文件存在
        ppt_dir = os.path.join(current_app.config.get('BASE_DIR', os.path.abspath(os.path.join(current_app.root_path, '..'))), 'ppt')
        ppt_file_path = os.path.join(ppt_dir, preview_file)
        if not os.path.isfile(ppt_file_path):
            return jsonify({'error': f'关联的PPT文件不存在: {preview_file}'}), 400

        # 保存封面图片（可选），没上传则自动从PPT第一页提取
        thumbnail_path = None
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            cover_ext = os.path.splitext(cover_file.filename)[1].lower()
            if cover_ext in ALLOWED_IMAGE_EXTENSIONS:
                thumb_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates', 'thumbnails')
                os.makedirs(thumb_dir, exist_ok=True)
                thumb_filename = f"analyzed_{uuid.uuid4().hex}{cover_ext}"
                thumbnail_path = os.path.join(thumb_dir, thumb_filename)
                cover_file.save(thumbnail_path)

        # 如果没有上传封面，创建默认缩略图（不自动提取，避免耗时过长）
        if not thumbnail_path:
            thumb_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates', 'thumbnails')
            os.makedirs(thumb_dir, exist_ok=True)
            thumb_filename = f"analyzed_default_{uuid.uuid4().hex}.png"
            thumbnail_path = os.path.join(thumb_dir, thumb_filename)
            create_default_thumbnail(thumbnail_path)

        # 创建模板记录并一次性提交
        template = Template(
            user_id=user_id,
            name=name,
            description=description,
            category=category,
            template_type='analyzed',
            file_path=ppt_file_path,
            thumbnail_path=thumbnail_path,
            template_info={
                'page_count': page_count,
                'placeholder_count': placeholder_count,
                'preview_file': preview_file,
                'is_analyzed': True,
            },
            is_public=False
        )
        db.session.add(template)
        db.session.commit()

        return jsonify({
            'message': '模板保存成功',
            'template': template.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'保存失败: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_templates():
    """获取模板列表 - 仅返回当前用户上传的模板"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        category = request.args.get('category', None)
        
        # 构建查询 - 查询当前用户上传的模板和分析模板
        query = Template.query.filter(
            Template.user_id == user_id,
            Template.template_type.in_(['uploaded', 'analyzed'])
        )
        
        # 按分类筛选
        if category:
            query = query.filter(Template.category == category)
        
        # 按创建时间倒序
        templates = query.order_by(Template.created_at.desc()).all()
        
        return jsonify({
            'templates': [t.to_dict() for t in templates],
            'categories': TEMPLATE_CATEGORIES
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """获取单个模板详情"""
    try:
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({'error': '模板不存在'}), 404
        
        return jsonify(template.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def upload_template():
    """上传模板"""
    print(f"[DEBUG] upload_template called")
    print(f"[DEBUG] Request files: {list(request.files.keys())}")
    print(f"[DEBUG] Request form: {list(request.form.keys())}")
    try:
        user_id = get_jwt_identity()
        print(f"[DEBUG] User ID: {user_id}")
        
        # 检查占位符模板文件（必传）
        if 'file' not in request.files:
            return jsonify({'error': '没有上传占位符模板文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择占位符模板文件'}), 400

        if not allowed_ppt_file(file.filename):
            return jsonify({'error': '只支持PPT/PPTX格式'}), 400

        # 原版模板文件（可选）
        original_file = request.files.get('original_file')
        original_file_path = None
        
        # 获取其他参数
        name = request.form.get('name', file.filename)
        description = request.form.get('description', '')
        category = request.form.get('category', 'other')
        template_info_raw = request.form.get('template_info', '')
        
        # 验证分类
        if category not in TEMPLATE_CATEGORIES:
            category = 'other'

        template_info = None
        if template_info_raw:
            try:
                import json
                template_info = json.loads(template_info_raw)
            except Exception:
                return jsonify({'error': 'template_info 格式错误，必须是合法JSON'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'templates',
            unique_filename
        )
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存占位符PPT文件
        file.save(file_path)

        # 保存原版模板文件（可选）
        if original_file and original_file.filename:
            if not allowed_ppt_file(original_file.filename):
                return jsonify({'error': '原版模板只支持PPT/PPTX格式'}), 400
            original_filename = secure_filename(original_file.filename)
            original_unique_filename = f"original_{uuid.uuid4().hex}_{original_filename}"
            original_file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'templates',
                original_unique_filename
            )
            original_file.save(original_file_path)

        # 获取源文件扩展名（处理没有扩展名的情况）
        _, ext = os.path.splitext(filename)
        source_extension = ext.lstrip('.').lower()

        # 如果是ppt，转换为pptx（用于后续解析与预览）
        if source_extension == 'ppt':
            try:
                converted_path = convert_ppt_to_pptx(file_path)
                if converted_path and os.path.exists(converted_path):
                    file_path = converted_path
            except Exception as e:
                print(f"[TEMPLATE] PPT 转换失败，继续使用原文件: {e}")

        # 先创建模板记录，拿到template.id后再导出每页图片
        template = Template(
            user_id=user_id,
            name=name,
            description=description,
            category=category,
            template_type='uploaded',
            file_path=file_path,
            thumbnail_path=None,
            styles=None,
            template_info=template_info,
            source_format=source_extension,
            is_public=False
        )
        db.session.add(template)
        db.session.flush()

        # 导出每页图片，第一页作为模板缩略图
        slide_images = []
        page_count = 0
        thumbnail_path = None
        try:
            png_paths = extract_template_slide_images(file_path, template.id)
            page_count = len(png_paths)
            for idx, png_path in enumerate(png_paths, start=1):
                rel_path = os.path.relpath(
                    png_path,
                    current_app.config['UPLOAD_FOLDER']
                ).replace('\\', '/')
                slide_images.append({
                    'page_number': idx,
                    'image_path': rel_path,
                })

            if png_paths:
                thumbnail_path = png_paths[0]
        except Exception as e:
            print(f"[TEMPLATE] 导出模板页图片失败: {e}")

        # 没有成功导出页图时，退回默认缩略图
        if not thumbnail_path:
            thumbnail_filename = f"thumb_{unique_filename}.png"
            thumbnail_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'templates',
                'thumbnails',
                thumbnail_filename
            )
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            create_default_thumbnail(thumbnail_path)

        template.thumbnail_path = thumbnail_path

        # 合并模板结构信息（页数、每页预览）
        base_template_info = template_info if isinstance(template_info, dict) else {}
        merged_template_info = {
            **base_template_info,
            'page_count': page_count,
            'slide_images': slide_images,
            'placeholder_template_path': file_path,
            'original_template_path': original_file_path,
        }
        template.template_info = merged_template_info

        # 解析模板样式
        print(f"[DEBUG] 解析模板样式: {file_path}")
        print(f"[DEBUG] ====== 开始解析 ======")
        template_styles = parse_template_styles(file_path)
        print(f"[DEBUG] ====== 解析完成 ======")
        print(f"[DEBUG] 解析到的样式: {template_styles}")
        
        # 保存到数据库
        template.styles = template_styles
        db.session.commit()
        
        return jsonify({
            'message': '模板上传成功',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Error uploading template: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@bp.route('/<template_id>/thumbnail', methods=['GET'])
@bp.route('/<template_id>/thumbnail/', methods=['GET'])
def get_template_thumbnail(template_id):
    """获取模板缩略图文件"""
    try:
        template = Template.query.get(template_id)

        if not template:
            return jsonify({'error': '模板不存在'}), 404

        if not template.thumbnail_path or not os.path.exists(template.thumbnail_path):
            return jsonify({'error': '缩略图不存在'}), 404

        return send_file(template.thumbnail_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>/slides/<int:page_number>/image', methods=['GET'])
@bp.route('/<template_id>/slides/<int:page_number>/image/', methods=['GET'])
def get_template_slide_image(template_id, page_number):
    """获取模板某一页预览图"""
    try:
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'error': '模板不存在'}), 404

        info = template.template_info or {}
        slide_images = info.get('slide_images') or []
        target = None
        for item in slide_images:
            if int(item.get('page_number', 0)) == int(page_number):
                target = item
                break

        if not target:
            return jsonify({'error': '该页预览图不存在'}), 404

        rel_path = target.get('image_path')
        if not rel_path:
            return jsonify({'error': '预览图路径无效'}), 404

        abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], rel_path)
        if not os.path.exists(abs_path):
            return jsonify({'error': '预览图文件不存在'}), 404

        return send_file(abs_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>/thumbnail', methods=['POST'])
@bp.route('/<template_id>/thumbnail/', methods=['POST'])
@jwt_required()
def upload_template_thumbnail(template_id):
    """上传模板预览图"""
    try:
        user_id = get_jwt_identity()
        template = Template.query.get(template_id)

        if not template:
            return jsonify({'error': '模板不存在'}), 404

        if template.user_id != user_id:
            return jsonify({'error': '无权限修改此模板'}), 403

        if 'thumbnail' not in request.files:
            return jsonify({'error': '没有上传缩略图文件'}), 400

        file = request.files['thumbnail']
        if file.filename == '':
            return jsonify({'error': '没有选择缩略图文件'}), 400

        if not allowed_image_file(file.filename):
            return jsonify({'error': '只支持 png/jpg/jpeg/gif 格式'}), 400

        thumb_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates', 'thumbnails')
        os.makedirs(thumb_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_thumb_name = f"thumb_custom_{template.id}_{uuid.uuid4().hex}.{ext}"
        new_thumb_path = os.path.join(thumb_dir, new_thumb_name)
        file.save(new_thumb_path)

        old_thumb = template.thumbnail_path
        template.thumbnail_path = new_thumb_path
        db.session.commit()

        try:
            if old_thumb and old_thumb != new_thumb_path and os.path.exists(old_thumb):
                os.remove(old_thumb)
        except Exception:
            pass

        return jsonify({'message': '缩略图上传成功', 'template': template.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>', methods=['PUT'])
@bp.route('/<template_id>/', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    """更新模板信息"""
    try:
        user_id = get_jwt_identity()
        
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'error': '模板不存在'}), 404
        
        # 检查权限：只能更新自己的模板
        if template.user_id != user_id:
            return jsonify({'error': '无权限修改此模板'}), 403
        
        # 获取更新数据
        data = request.get_json()
        
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'category' in data and data['category'] in TEMPLATE_CATEGORIES:
            template.category = data['category']
        if 'template_info' in data:
            template_info = data.get('template_info')
            if template_info is not None and not isinstance(template_info, dict):
                return jsonify({'error': 'template_info 必须为对象'}), 400
            template.template_info = template_info
        
        db.session.commit()
        
        return jsonify({
            'message': '模板更新成功',
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>', methods=['DELETE'])
@bp.route('/<template_id>/', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    """删除模板"""
    try:
        user_id = get_jwt_identity()
        
        template = Template.query.get(template_id)
        if not template:
            return jsonify({'error': '模板不存在'}), 404
        
        # 检查权限：只能删除自己的模板
        if template.user_id != user_id:
            return jsonify({'error': '无权限删除此模板'}), 403
        
        # 不能删除内置模板
        if template.template_type == 'builtin':
            return jsonify({'error': '不能删除内置模板'}), 403
        
        # 删除文件（analyzed类型不删除关联的PPT文件，只删缩略图）
        try:
            if template.template_type != 'analyzed':
                if os.path.exists(template.file_path):
                    os.remove(template.file_path)
            if template.thumbnail_path and os.path.exists(template.thumbnail_path):
                os.remove(template.thumbnail_path)

            info = template.template_info or {}
            slide_images = info.get('slide_images') or []
            for item in slide_images:
                rel_path = item.get('image_path')
                if not rel_path:
                    continue
                abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], rel_path)
                if os.path.exists(abs_path):
                    os.remove(abs_path)

            slides_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'templates', 'slides', str(template.id))
            if os.path.exists(slides_dir):
                shutil.rmtree(slides_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error deleting template files: {e}")
        
        # 从数据库删除
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': '模板删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>/preview', methods=['GET'])
@bp.route('/<template_id>/preview/', methods=['GET'])
@jwt_required()
def get_template_preview(template_id):
    """获取模板预览配置（OnlyOffice 只读预览）"""
    try:
        user_id = get_jwt_identity()
        template = Template.query.get(template_id)

        if not template:
            return jsonify({'error': '模板不存在'}), 404

        if template.user_id and template.user_id != user_id:
            return jsonify({'error': '无权限预览此模板'}), 403

        # 规范化文件路径
        file_path = os.path.normpath(template.file_path) if template.file_path else None
        if not file_path or not os.path.exists(file_path):
            print(f"[TEMPLATE] 预览失败: 文件不存在")
            print(f"[TEMPLATE]   - 原路径: {template.file_path}")
            print(f"[TEMPLATE]   - 规范化后: {file_path}")
            return jsonify({'error': '模板文件不存在'}), 404

        file_name = os.path.basename(file_path)

        # OnlyOffice配置
        onlyoffice_url = current_app.config.get('ONLYOFFICE_URL', 'http://localhost:80')
        jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')

        # 生成文件访问URL
        public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
        if not public_base_url:
            public_base_url = request.host_url.rstrip('/')

        # 文件下载URL（OnlyOffice需要能够访问这个URL来获取文件）
        file_url = f"{public_base_url}/api/templates/{template_id}/file"

        # 生成唯一的文档key（用于OnlyOffice缓存管理）
        import hashlib
        stat = os.stat(file_path)
        key_base = f"{template.id}_{stat.st_mtime}_{stat.st_size}"
        doc_key = hashlib.md5(key_base.encode()).hexdigest()

        # 构建完整的editor config（模板预览为只读模式）
        doc_config = {
            'fileType': 'pptx',
            'key': doc_key,
            'title': file_name,
            'url': file_url,
            'permissions': {
                'edit': False,
                'download': True,
                'print': True
            }
        }

        editor_cfg = {
            'lang': 'zh-CN',
            'mode': 'view',  # 只读预览模式
            'user': {
                'id': str(user_id),
                'name': 'User'
            }
        }

        # 生成JWT Token（如果配置了密钥）
        token = ''
        if jwt_secret:
            import jwt as pyjwt
            import time

            payload = {
                'document': doc_config,
                'documentType': 'presentation',
                'editorConfig': editor_cfg,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600
            }

            try:
                token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
                print(f"[ONLYOFFICE] 模板预览JWT生成成功，key={doc_key}")
            except Exception as e:
                print(f"[ONLYOFFICE] 模板预览JWT生成失败: {e}")
                token = ''

        return jsonify({
            'file_id': template.id,
            'file_name': file_name,
            'file_url': file_url,
            'key': doc_key,
            'onlyoffice_url': onlyoffice_url,
            'token': token,
            # 返回完整editor config供前端直接使用
            'document': doc_config,
            'editor_config': editor_cfg,
            'access_token': token,
            'access_token_ttl': 3600
        }), 200

    except Exception as e:
        print(f"Error getting template preview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>/file', methods=['GET'])
def get_template_file(template_id):
    """获取模板文件（供OnlyOffice访问）"""
    template = Template.query.get(template_id)
    if not template:
        return jsonify({'message': '模板不存在'}), 404

    # 规范化文件路径
    file_path = os.path.normpath(template.file_path) if template.file_path else None
    if not file_path or not os.path.exists(file_path):
        return jsonify({'message': '模板文件不存在'}), 404

    return send_file(file_path, as_attachment=False, download_name=os.path.basename(file_path))


@bp.route('/categories', methods=['GET'])
@bp.route('/categories/', methods=['GET'])
def get_categories():
    """获取所有模板分类"""
    return jsonify(TEMPLATE_CATEGORIES), 200


@bp.route('/<template_id>/cover', methods=['POST'])
@bp.route('/<template_id>/cover/', methods=['POST'])
@jwt_required()
def upload_template_cover(template_id):
    """上传模板封面图片"""
    try:
        user_id = get_jwt_identity()
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({'error': '模板不存在'}), 404
        
        # 检查权限
        if template.user_id and template.user_id != user_id:
            return jsonify({'error': '无权限修改此模板'}), 403
        
        if 'cover' not in request.files:
            return jsonify({'error': '请上传封面图片'}), 400
        
        cover_file = request.files['cover']
        if not cover_file or cover_file.filename == '':
            return jsonify({'error': '请选择封面图片'}), 400
        
        if not allowed_image_file(cover_file.filename):
            return jsonify({'error': '只支持PNG、JPG、JPEG、GIF格式的图片'}), 400
        
        # 保存封面图片
        filename = secure_filename(cover_file.filename)
        cover_filename = f"cover_{template_id}_{uuid.uuid4().hex}{os.path.splitext(filename)[1]}"
        cover_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'templates',
            'covers',
            cover_filename
        )
        os.makedirs(os.path.dirname(cover_path), exist_ok=True)
        cover_file.save(cover_path)
        
        # 删除旧封面
        if template.thumbnail_path and os.path.exists(template.thumbnail_path):
            try:
                os.remove(template.thumbnail_path)
            except:
                pass
        
        # 更新模板
        template.thumbnail_path = cover_path
        db.session.commit()
        
        return jsonify({
            'message': '封面上传成功',
            'thumbnail_path': cover_path
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<template_id>/extract-cover', methods=['POST'])
@bp.route('/<template_id>/extract-cover/', methods=['POST'])
@jwt_required()
def extract_template_cover(template_id):
    """从PPT第一页自动提取封面"""
    try:
        user_id = get_jwt_identity()
        template = Template.query.get(template_id)
        
        if not template:
            return jsonify({'error': '模板不存在'}), 404
        
        # 检查权限
        if template.user_id and template.user_id != user_id:
            return jsonify({'error': '无权限修改此模板'}), 403
        
        if not template.file_path or not os.path.exists(template.file_path):
            return jsonify({'error': '模板文件不存在'}), 404
        
        # 使用python-pptx提取第一页为图片
        try:
            from pptx import Presentation
            from PIL import Image
            import io
            
            # 打开PPT文件
            prs = Presentation(template.file_path)
            
            if len(prs.slides) == 0:
                return jsonify({'error': 'PPT文件没有幻灯片'}), 400
            
            # 获取第一张幻灯片
            first_slide = prs.slides[0]
            
            # 导出为图片
            # 创建临时目录
            temp_dir = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'templates',
                'temp',
                str(template_id)
            )
            os.makedirs(temp_dir, exist_ok=True)
            
            # 尝试导出幻灯片为图片
            # python-pptx不直接支持导出图片，需要使用其他方法
            # 先尝试使用LibreOffice转换
            from app.services.collabora_converter import convert_pptx_to_pngs
            png_paths = convert_pptx_to_pngs(template.file_path, temp_dir)
            
            if png_paths:
                # 使用第一页作为封面
                first_page_path = png_paths[0]
                
                # 保存封面
                cover_filename = f"cover_{template_id}_extracted.png"
                cover_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'templates',
                    'covers',
                    cover_filename
                )
                os.makedirs(os.path.dirname(cover_path), exist_ok=True)
                shutil.copy(first_page_path, cover_path)
                
                # 清理临时文件
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                # 删除旧封面
                if template.thumbnail_path and os.path.exists(template.thumbnail_path):
                    try:
                        os.remove(template.thumbnail_path)
                    except:
                        pass
                
                # 更新模板
                template.thumbnail_path = cover_path
                db.session.commit()
                
                return jsonify({
                    'message': '封面提取成功',
                    'thumbnail_path': cover_path
                }), 200
            else:
                # LibreOffice转换失败，创建默认封面
                # slide_width/slide_height 是 EMU 单位（1英寸=914400 EMU）
                # 转换为像素：假设 96 DPI
                slide_width_emu = prs.slide_width or 9144000  # 默认10英寸
                slide_height_emu = prs.slide_height or 6858000  # 默认7.5英寸
                slide_width_px = int(slide_width_emu / 914400 * 96)  # EMU -> 像素
                slide_height_px = int(slide_height_emu / 914400 * 96)
                
                # 限制最大尺寸，避免内存问题
                max_size = 1920
                if slide_width_px > max_size or slide_height_px > max_size:
                    scale = max_size / max(slide_width_px, slide_height_px)
                    slide_width_px = int(slide_width_px * scale)
                    slide_height_px = int(slide_height_px * scale)
                
                # 创建一个空白图片
                img = Image.new('RGB', (slide_width_px, slide_height_px), (255, 255, 255))
                
                # 保存为封面
                cover_filename = f"cover_{template_id}_default.png"
                cover_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'templates',
                    'covers',
                    cover_filename
                )
                os.makedirs(os.path.dirname(cover_path), exist_ok=True)
                img.save(cover_path)
                
                # 更新模板
                template.thumbnail_path = cover_path
                db.session.commit()
                
                return jsonify({
                    'message': '封面已创建（使用默认封面）',
                    'thumbnail_path': cover_path
                }), 200
                
        except ImportError:
            # python-pptx未安装，使用LibreOffice
            from app.services.collabora_converter import convert_pptx_to_pngs
            
            temp_dir = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'templates',
                'temp',
                str(template_id)
            )
            os.makedirs(temp_dir, exist_ok=True)
            
            png_paths = convert_pptx_to_pngs(template.file_path, temp_dir)
            
            if not png_paths:
                return jsonify({'error': '无法从PPT提取封面，请确保LibreOffice已安装或python-pptx库可用'}), 500
            
            # 使用第一页作为封面
            first_page_path = png_paths[0]
            
            # 保存封面
            cover_filename = f"cover_{template_id}_extracted.png"
            cover_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'templates',
                'covers',
                cover_filename
            )
            os.makedirs(os.path.dirname(cover_path), exist_ok=True)
            shutil.copy(first_page_path, cover_path)
            
            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # 删除旧封面
            if template.thumbnail_path and os.path.exists(template.thumbnail_path):
                try:
                    os.remove(template.thumbnail_path)
                except:
                    pass
            
            # 更新模板
            template.thumbnail_path = cover_path
            db.session.commit()
            
            return jsonify({
                'message': '封面提取成功',
                'thumbnail_path': cover_path
            }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

