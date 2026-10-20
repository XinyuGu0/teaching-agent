from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.ppt import PPT
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
import os
from datetime import datetime
import jwt
import uuid as uuid_lib

bp = Blueprint('ppt', __name__)


def _ensure_ppt_file(ppt):
    if ppt.file_path and os.path.exists(ppt.file_path):
        return ppt.file_path

    try:
        os.makedirs(current_app.config['GENERATED_PPTS_DIR'], exist_ok=True)
        safe_title = ''.join(c for c in (ppt.title or 'ppt') if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        filename = f"{safe_title or 'ppt'}.pptx"
        file_path = os.path.join(current_app.config['GENERATED_PPTS_DIR'], filename)

        prs = Presentation()
        blank_layout = prs.slide_layouts[6]

        for slide_data in (ppt.slides_data or []):
            slide = prs.slides.add_slide(blank_layout)

            bg = slide.background
            if isinstance(slide_data, dict) and isinstance(slide_data.get('background'), dict):
                color = slide_data['background'].get('color')
                if color:
                    try:
                        fill = bg.fill
                        fill.solid()
                        fill.fore_color.rgb = RGBColor.from_string(color)
                    except Exception:
                        pass

            for obj in slide_data.get('objects', []):
                if obj.get('type') == 'text':
                    opts = obj.get('options', {})
                    x = opts.get('x', 1)
                    y = opts.get('y', 1)
                    w = opts.get('w', 6)
                    h = opts.get('h', 1)
                    textbox = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
                    textbox.text_frame.text = obj.get('text', '')
                elif obj.get('type') == 'image':
                    opts = obj.get('options', {})
                    x = opts.get('x', 1)
                    y = opts.get('y', 1)
                    w = opts.get('w', 3)
                    h = opts.get('h', 3)
                    image_path = obj.get('path')
                    if image_path and os.path.exists(image_path):
                        try:
                            slide.shapes.add_picture(image_path, Inches(x), Inches(y), Inches(w), Inches(h))
                        except Exception:
                            pass

        prs.save(file_path)
        ppt.file_path = file_path
        db.session.commit()
        return file_path
    except Exception:
        return None


@bp.route('/<ppt_id>', methods=['GET'])
@jwt_required()
def get_ppt(ppt_id):
    """获取PPT详情"""
    current_user_id = get_jwt_identity()

    ppt = PPT.query.filter_by(id=ppt_id, user_id=current_user_id).first()

    if not ppt:
        return jsonify({'message': 'PPT不存在'}), 404

    return jsonify(ppt.to_dict()), 200


@bp.route('', methods=['GET'])
@jwt_required()
def list_ppts():
    """获取用户的所有PPT"""
    current_user_id = get_jwt_identity()

    ppts = PPT.query.filter_by(user_id=current_user_id).order_by(PPT.created_at.desc()).all()

    return jsonify({
        'ppts': [ppt.to_dict() for ppt in ppts]
    }), 200


@bp.route('/<ppt_id>', methods=['PUT'])
@jwt_required()
def update_ppt(ppt_id):
    """更新PPT"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    ppt = PPT.query.filter_by(id=ppt_id, user_id=current_user_id).first()

    if not ppt:
        return jsonify({'message': 'PPT不存在'}), 404

    # 更新字段
    if 'title' in data:
        ppt.title = data['title']
    if 'theme' in data:
        ppt.theme = data['theme']
    if 'slides_data' in data:
        ppt.slides_data = data['slides_data']
    if 'outline' in data:
        ppt.outline = data['outline']
    if 'status' in data:
        ppt.status = data['status']

    db.session.commit()

    return jsonify(ppt.to_dict()), 200


@bp.route('/<ppt_id>', methods=['DELETE'])
@jwt_required()
def delete_ppt(ppt_id):
    """删除PPT"""
    current_user_id = get_jwt_identity()

    ppt = PPT.query.filter_by(id=ppt_id, user_id=current_user_id).first()

    if not ppt:
        return jsonify({'message': 'PPT不存在'}), 404

    db.session.delete(ppt)
    db.session.commit()

    return jsonify({'message': 'PPT已删除'}), 200


@bp.route('/<ppt_id>/download', methods=['GET'])
@jwt_required()
def download_ppt(ppt_id):
    """下载PPT文件"""
    current_user_id = get_jwt_identity()

    ppt = PPT.query.filter_by(id=ppt_id, user_id=current_user_id).first()
    if not ppt:
        return jsonify({'message': 'PPT不存在'}), 404

    file_path = _ensure_ppt_file(ppt)
    if not file_path or not os.path.exists(file_path):
        return jsonify({'message': 'PPT文件不存在'}), 404

    response = send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@bp.route('/<ppt_id>/wopi', methods=['GET'])
@jwt_required()
def get_wopi_info(ppt_id):
    """获取OnlyOffice访问配置"""
    current_user_id = get_jwt_identity()

    ppt = PPT.query.filter_by(id=ppt_id, user_id=current_user_id).first()
    if not ppt:
        return jsonify({'message': 'PPT不存在'}), 404

    file_path = _ensure_ppt_file(ppt)
    if not file_path or not os.path.exists(file_path):
        return jsonify({'message': 'PPT文件不存在'}), 404

    file_name = os.path.basename(file_path)
    
    # OnlyOffice配置
    onlyoffice_url = current_app.config.get('ONLYOFFICE_URL', 'http://localhost:80')
    jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')
    
    # 生成文件访问URL
    public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
    if not public_base_url:
        public_base_url = request.host_url.rstrip('/')
    
    # 文件下载URL（OnlyOffice需要能够访问这个URL来获取文件）
    file_url = f"{public_base_url}/api/ppts/{ppt_id}/file"
    
    # 生成唯一的文档key（用于OnlyOffice缓存管理）
    import hashlib
    stat = os.stat(file_path)
    key_base = f"{ppt.id}_{stat.st_mtime}_{stat.st_size}"
    doc_key = hashlib.md5(key_base.encode()).hexdigest()
    
    # 生成回调URL
    callback_url = f"{public_base_url}/api/ppts/{ppt_id}/callback"
    
    # 构建完整的editor config（必须与JWT payload完全一致）
    doc_config = {
        'fileType': 'pptx',
        'key': doc_key,
        'title': file_name,
        'url': file_url,
        'permissions': {
            'edit': True,
            'download': True,
            'print': True
        }
    }
    
    editor_cfg = {
        'callbackUrl': callback_url,
        'lang': 'zh-CN',
        'mode': 'edit',
        'user': {
            'id': str(current_user_id),
            'name': 'User'
        }
    }
    
    # 生成JWT Token（如果配置了密钥)
    token = ''
    if jwt_secret:
        import jwt as pyjwt
        import time
        
        # ONLYOFFICE要求的JWT payload格式
        # 注意：payload必须与前端传给DocsAPI.DocEditor的config完全一致
        # documentType对于PPT必须是'presentation'（不是'slide'）
        payload = {
            'document': doc_config,
            'documentType': 'presentation',
            'editorConfig': editor_cfg,
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600
        }
        
        try:
            token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
            # PyJWT 2.x返回字符串，1.x返回bytes
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            current_app.logger.info(f"[ONLYOFFICE] JWT生成成功，key={doc_key}")
        except Exception as e:
            current_app.logger.error(f"[ONLYOFFICE] JWT生成失败: {e}")
            token = ''
    
    return jsonify({
        'file_id': ppt.id,
        'file_name': file_name,
        'file_url': file_url,
        'key': doc_key,
        'onlyoffice_url': onlyoffice_url,
        'token': token,
        'callback_url': callback_url,
        # 返回完整editor config供前端直接使用
        'document': doc_config,
        'editor_config': editor_cfg,
        'wopi_src': file_url,
        'access_token': token,
        'access_token_ttl': 3600
    }), 200


@bp.route('/<ppt_id>/file', methods=['GET'])
def get_ppt_file(ppt_id):
    """获取PPT文件（供OnlyOffice访问）"""
    # 支持通过token参数验证
    token = request.args.get('token', '')
    
    ppt = PPT.query.filter_by(id=ppt_id).first()
    if not ppt:
        return jsonify({'message': 'PPT不存在'}), 404

    file_path = _ensure_ppt_file(ppt)
    if not file_path or not os.path.exists(file_path):
        return jsonify({'message': 'PPT文件不存在'}), 404

    return send_file(file_path, as_attachment=False, download_name=os.path.basename(file_path))


@bp.route('/wopi/files/<file_id>', methods=['GET'])
def wopi_check_file_info(file_id):
    """WOPI CheckFileInfo"""
    access_token = request.args.get('access_token', '')
    if not access_token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.lower().startswith('bearer '):
            access_token = auth_header.split(' ', 1)[1].strip()

    if not access_token:
        return jsonify({'message': '缺少access_token'}), 400

    token_data = verify_wopi_token(access_token)
    if not token_data or token_data.get('file_id') != file_id or token_data.get('file_type') != 'ppt':
        return jsonify({'message': '无效的access_token'}), 401

    ppt = PPT.query.filter_by(id=file_id, user_id=token_data.get('user_id')).first()
    if not ppt or not ppt.file_path or not os.path.exists(ppt.file_path):
        return jsonify({'message': 'PPT不存在'}), 404

    stat = os.stat(ppt.file_path)
    return jsonify({
        'BaseFileName': os.path.basename(ppt.file_path),
        'Size': stat.st_size,
        'OwnerId': ppt.user_id,
        'UserId': token_data.get('user_id'),
        'Version': str(ppt.version or 1),
        'LastModifiedTime': datetime.utcfromtimestamp(stat.st_mtime).isoformat() + 'Z',
        'UserCanWrite': True,
        'SupportsUpdate': True,
        'SupportsGetLock': False,
        'SupportsLocks': False,
        'SupportsRename': False,
        'ReadOnly': False,
        'IsAnonymousUser': False,
        'UserFriendlyName': 'User',
        'SupportsGetFile': True
    }), 200


@bp.route('/wopi/files/<file_id>/contents', methods=['GET'])
def wopi_get_file_contents(file_id):
    """WOPI GetFile"""
    access_token = request.args.get('access_token', '')
    if not access_token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.lower().startswith('bearer '):
            access_token = auth_header.split(' ', 1)[1].strip()

    if not access_token:
        return jsonify({'message': '缺少access_token'}), 400

    token_data = verify_wopi_token(access_token)
    if not token_data or token_data.get('file_id') != file_id or token_data.get('file_type') != 'ppt':
        return jsonify({'message': '无效的access_token'}), 401

    ppt = PPT.query.filter_by(id=file_id, user_id=token_data.get('user_id')).first()
    if not ppt or not ppt.file_path or not os.path.exists(ppt.file_path):
        return jsonify({'message': 'PPT不存在'}), 404

    return send_file(ppt.file_path, as_attachment=False, download_name=os.path.basename(ppt.file_path))


@bp.route('/wopi/files/<file_id>/contents', methods=['POST'])
def wopi_put_file_contents(file_id):
    """WOPI PutFile"""
    access_token = request.args.get('access_token', '')
    if not access_token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.lower().startswith('bearer '):
            access_token = auth_header.split(' ', 1)[1].strip()

    if not access_token:
        return jsonify({'message': '缺少access_token'}), 400

    token_data = verify_wopi_token(access_token)
    if not token_data or token_data.get('file_id') != file_id or token_data.get('file_type') != 'ppt':
        return jsonify({'message': '无效的access_token'}), 401

    ppt = PPT.query.filter_by(id=file_id, user_id=token_data.get('user_id')).first()
    if not ppt or not ppt.file_path:
        return jsonify({'message': 'PPT不存在'}), 404

    os.makedirs(os.path.dirname(ppt.file_path), exist_ok=True)

    with open(ppt.file_path, 'wb') as f:
        f.write(request.get_data())

    try:
        prs = Presentation(ppt.file_path)
        ppt.slides_data = []
        for idx, slide in enumerate(prs.slides, start=1):
            ppt.slides_data.append({
                'slide_number': idx,
                'layout': 'content',
                'background': {'color': 'FFFFFF'},
                'objects': []
            })
    except Exception:
        pass

    ppt.version = (ppt.version or 1) + 1
    ppt.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'OK'}), 200


@bp.route('/<ppt_id>/callback', methods=['POST'])
def onlyoffice_callback(ppt_id):
    """ONLYOFFICE保存回调"""
    try:
        data = request.get_json()
        current_app.logger.info(f"[ONLYOFFICE] 收到回调: ppt_id={ppt_id}, data={data}")
        
        # 验证JWT token（如果启用）
        jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')
        if jwt_secret:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]
                try:
                    import jwt as pyjwt
                    pyjwt.decode(token, jwt_secret, algorithms=['HS256'])
                except Exception as e:
                    current_app.logger.error(f"[ONLYOFFICE] JWT验证失败: {e}")
                    return jsonify({'error': 1, 'message': 'Invalid token'}), 401
        
        status = data.get('status')
        
        # status=1: 文档正在编辑
        # status=2: 文档准备保存
        # status=3: 文档保存出错
        # status=4: 文档关闭无修改
        # status=6: 文档正在编辑，但当前用户已保存
        # status=7: 强制保存出错
        
        if status == 2 or status == 6:
            # 下载编辑后的文件
            download_url = data.get('url')
            if download_url:
                ppt = PPT.query.get(ppt_id)
                if ppt and ppt.file_path:
                    import requests
                    response = requests.get(download_url, timeout=30)
                    if response.status_code == 200:
                        os.makedirs(os.path.dirname(ppt.file_path), exist_ok=True)
                        with open(ppt.file_path, 'wb') as f:
                            f.write(response.content)
                        
                        # 更新版本号
                        ppt.version = (ppt.version or 1) + 1
                        ppt.updated_at = datetime.utcnow()
                        db.session.commit()
                        
                        current_app.logger.info(f"[ONLYOFFICE] 文件保存成功: {ppt.file_path}")
                        return jsonify({'error': 0}), 200
        
        # 其他状态直接返回成功
        return jsonify({'error': 0}), 200
        
    except Exception as e:
        current_app.logger.error(f"[ONLYOFFICE] 回调处理失败: {e}")
        return jsonify({'error': 1, 'message': str(e)}), 500
