from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from werkzeug.utils import secure_filename
import os
import uuid
import mimetypes
from app.extensions import db
from app.models.document import Document
from app.tasks.background_tasks import process_document_task
from app.utils.wopi import generate_wopi_token, verify_wopi_token, get_collabora_app_path
from datetime import datetime

bp = Blueprint('document', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return ext in allowed

@bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """List user documents"""
    current_user_id = get_jwt_identity()
    documents = Document.query.filter_by(user_id=current_user_id).order_by(Document.created_at.desc()).all()

    return jsonify({
        'documents': [doc.to_dict() for doc in documents]
    }), 200


@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload documents (supports multiple files)"""
    current_user_id = get_jwt_identity()
    
    print(f'[DEBUG UPLOAD] ========== 文件上传请求 ==========')
    print(f'[DEBUG UPLOAD] User ID: {current_user_id}')
    print(f'[DEBUG UPLOAD] Request files: {list(request.files.keys())}')
    print(f'[DEBUG UPLOAD] Request form: {list(request.form.keys())}')
    
    # 支持单数和复数字段名：'file' 或 'files'
    files = None
    if 'files' in request.files:
        files = request.files.getlist('files')
    elif 'file' in request.files:
        files = [request.files['file']]
    else:
        print('[DEBUG UPLOAD] 错误: 没有找到file或files字段')
        return jsonify({'error': '没有文件'}), 400
    
    conversation_id = request.form.get('conversation_id')
    print(f'[DEBUG UPLOAD] Conversation ID: {conversation_id}')
    
    print(f'[DEBUG UPLOAD] 文件数量: {len(files)}')
    print(f'[DEBUG UPLOAD] Conversation ID: {conversation_id}')

    if not files:
        print('[DEBUG UPLOAD] 错误: 文件列表为空')
        return jsonify({'error': '文件列表为空'}), 400

    uploaded_documents = []

    for idx, file in enumerate(files):
        print(f'[DEBUG UPLOAD] 处理文件 {idx+1}/{len(files)}: {file.filename}')
        
        if file.filename == '':
            print('[DEBUG UPLOAD] 跳过空文件名')
            continue

        # 检查文件去重（基于原始文件名）
        existing_doc = Document.query.filter_by(
            user_id=current_user_id,
            original_filename=file.filename,
            status='ready'
        ).first()
        
        if existing_doc:
            print(f'[DEBUG UPLOAD] 文件已存在，跳过上传: {file.filename}')
            print(f'[DEBUG UPLOAD] 已存在文档ID: {existing_doc.id}')
            # 跳过已存在的文件，继续处理其他文件
            continue

        if not allowed_file(file.filename):
            print(f'[DEBUG UPLOAD] 错误: 不支持的文件类型 - {file.filename}')
            return jsonify({'error': f'不支持的文件类型: {file.filename}'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        print(f'[DEBUG UPLOAD] 文件大小: {file_size} bytes')

        max_size = current_app.config.get('UPLOAD_MAX_SIZE', 10 * 1024 * 1024)
        if file_size > max_size:
            print(f'[DEBUG UPLOAD] 错误: 文件超过大小限制 ({max_size} bytes)')
            return jsonify({'error': f'文件 {file.filename} 大小超过限制'}), 400

        # Generate unique filename
        # 不使用secure_filename()，因为它会清除特殊字符，导致文件名丢失
        # 只做基本的安全检查
        original_filename = file.filename
        
        # 安全地获取文件扩展名（从原始文件名）
        if '.' not in original_filename:
            # 如果没有扩展名，添加一个默认的
            ext = 'txt'
            unique_filename = f"{uuid.uuid4()}.{ext}"
        else:
            ext = original_filename.rsplit('.', 1)[1].lower()
            # 只保留基本字母数字和扩展名
            safe_filename = ''.join(c for c in original_filename if c.isalnum() or c in '._- ')
            if not safe_filename:
                safe_filename = f"file_{uuid.uuid4()}"
            unique_filename = f"{safe_filename}_{uuid.uuid4()}.{ext}"

        # Create user upload directory
        user_upload_dir = os.path.join(current_app.config.get('USER_UPLOADS_DIR', 'uploads'), current_user_id)
        os.makedirs(user_upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(user_upload_dir, unique_filename)
        file.save(file_path)

        # Determine file type
        file_type_map = {
            'pdf': 'pdf',
            'doc': 'word', 'docx': 'word',
            'ppt': 'ppt', 'pptx': 'ppt',
            'xls': 'excel', 'xlsx': 'excel',
            'txt': 'text', 'md': 'text',
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
            'mp4': 'video', 'avi': 'video', 'mov': 'video',
            'mp3': 'audio', 'wav': 'audio', 'm4a': 'audio', 'ogg': 'audio', 'flac': 'audio', 'aac': 'audio'
        }
        file_type = file_type_map.get(ext, 'other')

        # Create document record
        document = Document(
            user_id=current_user_id,
            filename=unique_filename,
            original_filename=original_filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            status='processing'
        )

        db.session.add(document)
        db.session.commit()  # 必须先提交，否则处理任务找不到文档
        print('[DEBUG UPLOAD] ========== 开始处理文档 ==========')
        print(f'[DEBUG UPLOAD] 文件名: {original_filename}')
        print(f'[DEBUG UPLOAD] 文件ID: {document.id}')
        print(f'[DEBUG UPLOAD] 文件类型: {file_type}')
        print(f'[DEBUG UPLOAD] 文件大小: {file_size} bytes')
        print(f'[DEBUG UPLOAD] Conversation ID: {conversation_id}')
        print(f'[DEBUG UPLOAD] 文件路径: {file_path}')
        print('[DEBUG UPLOAD] =======================================')

        # 直接同步处理，不使用Celery（确保文件被处理）
        import time
        start_time = time.time()
        print(f"[DEBUG] 开始同步处理文档 {document.id}...")
        
        try:
            # 直接调用任务函数（同步）
            from app.tasks.background_tasks import process_document_task
            process_document_task(document.id, conversation_id)
            
            elapsed_time = time.time() - start_time
            print(f"[DEBUG] ✓ 文档 {document.id} 处理完成，耗时: {elapsed_time:.2f}秒")
        except Exception as sync_error:
            print(f"[ERROR] 同步处理失败: {sync_error}")
            import traceback
            traceback.print_exc()
            # 即使失败也标记为ready
            document.status = 'ready'
            db.session.commit()

        # 提取文本内容返回给前端（用于AI对话展示）
        extracted_text = ''
        try:
            from app.utils import file_processor
            extracted_text = file_processor.extract_text(file_path, file_type)
            # 截取前2000字符，避免返回过多数据
            if len(extracted_text) > 2000:
                extracted_text = extracted_text[:2000] + '\n\n...(内容过长，已截断)'
            print(f"[DEBUG UPLOAD] 提取文本内容: {len(extracted_text)} 字符")
        except Exception as extract_err:
            print(f"[DEBUG UPLOAD] 文本提取失败: {extract_err}")

        doc_dict = document.to_dict()
        doc_dict['extracted_text'] = extracted_text
        uploaded_documents.append(doc_dict)

    db.session.commit()

    return jsonify({
        'message': f'成功上传 {len(uploaded_documents)} 个文件',
        'documents': uploaded_documents
    }), 201


@bp.route('/<document_id>/preview', methods=['GET'])
@jwt_required(optional=True)
def preview_document(document_id):
    """Preview document (inline)"""
    current_user_id = get_jwt_identity()

    if not current_user_id:
        auth_header = request.headers.get('Authorization', '')
        token = ''
        if auth_header.lower().startswith('bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        else:
            token = request.args.get('token', '')

        if token:
            try:
                token_data = decode_token(token)
                current_user_id = token_data.get('sub') or token_data.get('identity')
            except Exception:
                current_user_id = None

    if not current_user_id:
        return jsonify({'error': '未授权'}), 401

    # 兼容JWT里sub可能是int/str，优先按文档ID查，再校验归属
    document = Document.query.filter_by(id=document_id).first()

    if not document:
        return jsonify({'error': '文档不存在'}), 404

    if str(document.user_id) != str(current_user_id):
        return jsonify({'error': '无权访问该文档'}), 403

    if not os.path.exists(document.file_path):
        # 兼容历史路径变化：尝试按当前配置恢复实际文件路径
        user_upload_dir = os.path.join(current_app.config.get('USER_UPLOADS_DIR', 'uploads'), str(document.user_id))
        candidate_paths = [
            os.path.join(user_upload_dir, document.filename or ''),
            os.path.join(user_upload_dir, os.path.basename(document.file_path or '')),
        ]

        recovered_path = next((p for p in candidate_paths if p and os.path.exists(p)), None)
        if recovered_path:
            document.file_path = recovered_path
            db.session.commit()
        else:
            return jsonify({'error': '文件不存在'}), 404

    mime_type, _ = mimetypes.guess_type(document.file_path)
    response = send_file(document.file_path, mimetype=mime_type, as_attachment=False)
    # 避免中文文件名写入Header导致开发服务器latin-1编码报错
    response.headers['Content-Disposition'] = 'inline'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@bp.route('/<document_id>/wopi', methods=['GET'])
@jwt_required()
def get_document_wopi(document_id):
    """获取文档WOPI配置"""
    current_user_id = get_jwt_identity()

    document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
    if not document:
        return jsonify({'message': '文档不存在'}), 404

    if not document.file_path or not os.path.exists(document.file_path):
        return jsonify({'message': '文档文件不存在'}), 404

    ext = ''
    if '.' in document.filename:
        ext = document.filename.rsplit('.', 1)[1].lower()

    token = generate_wopi_token(document.id, current_user_id, ext or 'docx')
    collabora_url = current_app.config.get('WOPI_BASE_URL')

    file_name = document.original_filename
    access_token_ttl = current_app.config.get('WOPI_TOKEN_TTL', 3600)

    wopi_host = current_app.config.get('WOPI_HOST', '').strip()
    public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()

    if wopi_host:
        wopi_host = wopi_host.rstrip('/')
    if public_base_url:
        public_base_url = public_base_url.rstrip('/')

    base_for_wopi = wopi_host or public_base_url or request.host_url.rstrip('/')
    wopi_src = f"{base_for_wopi}/api/documents/wopi/files/{document.id}"

    app_path = get_collabora_app_path(collabora_url, ext or 'docx')

    return jsonify({
        'file_id': document.id,
        'file_name': file_name,
        'wopi_src': wopi_src,
        'access_token': token,
        'access_token_ttl': access_token_ttl,
        'collabora_url': collabora_url,
        'collabora_app_path': app_path
    }), 200


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
    if not token_data or token_data.get('file_id') != file_id:
        return jsonify({'message': '无效的access_token'}), 401

    document = Document.query.filter_by(id=file_id, user_id=token_data.get('user_id')).first()
    if not document or not document.file_path or not os.path.exists(document.file_path):
        return jsonify({'message': '文档不存在'}), 404

    stat = os.stat(document.file_path)
    return jsonify({
        'BaseFileName': document.original_filename,
        'Size': stat.st_size,
        'OwnerId': document.user_id,
        'UserId': token_data.get('user_id'),
        'Version': '1',
        'LastModifiedTime': datetime.utcfromtimestamp(stat.st_mtime).isoformat() + 'Z',
        'UserCanWrite': False,
        'SupportsUpdate': False,
        'SupportsGetLock': False,
        'SupportsLocks': False,
        'SupportsRename': False,
        'ReadOnly': True,
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
    if not token_data or token_data.get('file_id') != file_id:
        return jsonify({'message': '无效的access_token'}), 401

    document = Document.query.filter_by(id=file_id, user_id=token_data.get('user_id')).first()
    if not document or not document.file_path or not os.path.exists(document.file_path):
        return jsonify({'message': '文档不存在'}), 404

    return send_file(document.file_path, as_attachment=False, download_name=document.original_filename)


@bp.route('/<document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete document"""
    current_user_id = get_jwt_identity()
    document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()

    if not document:
        return jsonify({'error': '文档不存在'}), 404

    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.session.delete(document)
    db.session.commit()

    return jsonify({'message': '文档已删除'}), 200


@bp.route('/<document_id>/onlyoffice', methods=['GET'])
@jwt_required()
def get_document_onlyoffice_config(document_id):
    """获取文档的OnlyOffice只读预览配置"""
    current_user_id = get_jwt_identity()
    
    document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
    if not document:
        return jsonify({'message': '文档不存在'}), 404
    
    if not document.file_path or not os.path.exists(document.file_path):
        return jsonify({'message': '文件不存在'}), 404
    
    # 确定文件类型
    file_ext = os.path.splitext(document.file_path)[1].lower().lstrip('.')
    
    # OnlyOffice documentType mapping
    doc_type_map = {
        'doc': 'word', 'docx': 'word', 'odt': 'word', 'txt': 'word', 'rtf': 'word',
        'xls': 'cell', 'xlsx': 'cell', 'ods': 'cell', 'csv': 'cell',
        'ppt': 'slide', 'pptx': 'slide', 'odp': 'slide',
        'pdf': 'word'
    }
    doc_type = doc_type_map.get(file_ext, 'word')
    
    onlyoffice_url = current_app.config.get('ONLYOFFICE_URL', 'http://localhost:80')
    jwt_secret = current_app.config.get('ONLYOFFICE_JWT_SECRET', '')
    
    public_base_url = current_app.config.get('PUBLIC_BASE_URL', '').strip()
    if not public_base_url:
        public_base_url = request.host_url.rstrip('/')
    # OnlyOffice在Docker中无法解析localhost，替换为127.0.0.1
    public_base_url = public_base_url.replace('localhost', '127.0.0.1')
    
    file_name = os.path.basename(document.file_path)
    # 使用无需JWT的serve路由，OnlyOffice无法携带JWT
    file_url = f"{public_base_url}/api/documents/serve/{document_id}"
    
    # 生成唯一key（加入时间戳防止OnlyOffice缓存）
    import hashlib
    import time as _time
    stat = os.stat(document.file_path)
    key_base = f"{document_id}_{stat.st_mtime}_{stat.st_size}_{int(_time.time())}"
    doc_key = hashlib.md5(key_base.encode()).hexdigest()
    
    doc_config = {
        'fileType': file_ext,
        'key': doc_key,
        'title': document.original_filename or file_name,
        'url': file_url,
        'permissions': {
            'edit': False,
            'download': True,
            'print': True,
            'review': False,
            'fillForms': False,
            'comment': False,
            'modifyFilter': False,
            'modifyContentControl': False,
            'copy': True
        }
    }
    
    editor_cfg = {
        'lang': 'zh-CN',
        'mode': 'view',
        'user': {
            'id': str(current_user_id),
            'name': 'User'
        }
    }
    
    token = ''
    if jwt_secret:
        try:
            import jwt as pyjwt
            import time
            payload = {
                'document': doc_config,
                'documentType': doc_type,
                'editorConfig': editor_cfg,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600
            }
            token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
            if isinstance(token, bytes):
                token = token.decode('utf-8')
        except Exception as e:
            current_app.logger.error(f"JWT生成失败: {e}")
    
    return jsonify({
        'document': doc_config,
        'documentType': doc_type,
        'editor_config': editor_cfg,
        'token': token,
        'onlyoffice_url': onlyoffice_url,
        'file_name': document.original_filename or file_name
    }), 200


@bp.route('/serve/<document_id>', methods=['GET'])
def serve_document(document_id):
    """无需JWT的文件服务路由，供OnlyOffice下载文件使用"""
    document = Document.query.filter_by(id=document_id).first()
    if not document:
        return jsonify({'message': '文档不存在'}), 404

    if not document.file_path or not os.path.exists(document.file_path):
        # 兼容历史路径变化
        user_upload_dir = os.path.join(current_app.config.get('USER_UPLOADS_DIR', 'uploads'), str(document.user_id))
        candidate_paths = [
            os.path.join(user_upload_dir, document.filename or ''),
            os.path.join(user_upload_dir, os.path.basename(document.file_path or '')),
        ]
        recovered_path = next((p for p in candidate_paths if p and os.path.exists(p)), None)
        if recovered_path:
            document.file_path = recovered_path
            db.session.commit()
        else:
            return jsonify({'message': '文件不存在'}), 404

    mime_type, _ = mimetypes.guess_type(document.file_path)
    response = send_file(document.file_path, mimetype=mime_type, as_attachment=False)
    response.headers['Content-Disposition'] = 'inline'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response