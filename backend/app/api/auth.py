from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from pathlib import Path
from difflib import SequenceMatcher
import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()

    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    # Find user
    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)

    return jsonify({'access_token': access_token}), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': user.to_dict()}), 200


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户画像信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'profile': {
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'teacher_gender': user.teacher_gender,
        'teacher_age': user.teacher_age,
        'school_name': user.school_name,
        'subject_category': user.subject_category,
        'courses': user.courses or [],
        'teaching_styles': user.teaching_styles or []
    }}), 200


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户画像信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}

    user.nickname = data.get('nickname')
    user.avatar_url = data.get('avatar_url')
    user.teacher_gender = data.get('teacher_gender')
    user.teacher_age = data.get('teacher_age')
    user.school_name = data.get('school_name')
    user.subject_category = data.get('subject_category')
    user.courses = data.get('courses', [])
    user.teaching_styles = data.get('teaching_styles', [])

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200


def _load_local_schools():
    """优先加载教育部CSV名单，回退txt名单"""
    base_dir = Path(current_app.root_path).parent

    # 1) 优先：用户提供的CSV（中文官方名单）
    csv_file = base_dir / '全国普通高等学校名单.csv'
    if csv_file.exists():
        import csv
        names = []
        with csv_file.open('r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                seq = (row[0] or '').strip()
                name = (row[1] or '').replace('\n', '').strip()
                # 只取正式数据行：序号为数字，且有学校名称
                if not seq.isdigit() or not name:
                    continue
                names.append(name)

        # 去重保序
        dedup = []
        seen = set()
        for n in names:
            if n not in seen:
                seen.add(n)
                dedup.append(n)
        if dedup:
            return dedup

    # 2) 回退：txt名单
    txt_file = base_dir / 'data' / 'schools_cn.txt'
    if txt_file.exists():
        return [line.strip() for line in txt_file.read_text(encoding='utf-8').splitlines() if line.strip()]

    return []


def _query_school_api(keyword):
    """调用免费学校查询接口（失败返回空）"""
    if not keyword:
        return []

    # 公开接口：大学信息（Hipolabs）
    # 只作为免费补充来源，返回英文名称，前端可直接展示
    try:
        params = urlencode({'search': keyword, 'country': 'China'})
        url = f"http://universities.hipolabs.com/search?{params}"
        with urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
        names = []
        for item in data or []:
            name = (item or {}).get('name')
            if name:
                names.append(name.strip())
        # 去重保序
        dedup = []
        seen = set()
        for n in names:
            if n not in seen:
                seen.add(n)
                dedup.append(n)
        return dedup[:20]
    except Exception:
        return []


@bp.route('/schools/suggest', methods=['GET'])
@jwt_required()
def suggest_schools():
    """学校/单位模糊搜索建议（仅返回本地中文名称，离线优先）"""
    keyword = (request.args.get('q') or '').strip()

    # 仅使用本地中文库，保证中文结果
    schools = _load_local_schools()
    if not keyword:
        return jsonify({'schools': schools[:20]}), 200

    kw = keyword.lower()

    # 1) 先收集包含命中，短关键词时放宽返回，提升“模糊联想”体验
    contains = [s for s in schools if kw in s.lower()]
    if len(keyword) <= 1:
        return jsonify({'schools': contains[:30]}), 200

    # 2) 综合打分：前缀命中 > 包含命中 > 相似度
    ranked = []
    for s in schools:
        s_lower = s.lower()
        ratio = SequenceMatcher(None, kw, s_lower).ratio()
        if ratio < 0.24 and kw not in s_lower:
            continue

        score = ratio
        if kw in s_lower:
            score += 0.35
        if s_lower.startswith(kw):
            score += 0.45
        # 关键词越短且完整包含时，适当再加权
        if kw in s_lower and len(keyword) <= 3:
            score += 0.12

        ranked.append((score, s))

    ranked.sort(key=lambda x: x[0], reverse=True)

    merged = []
    seen = set()
    # 优先包含命中，再补充综合排序结果
    for name in contains + [s for _, s in ranked]:
        if name not in seen:
            seen.add(name)
            merged.append(name)

    return jsonify({'schools': merged[:30]}), 200


@bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """上传用户头像"""
    current_app.logger.info('=== 开始处理头像上传 ===')
    current_user_id = get_jwt_identity()
    current_app.logger.info(f'用户ID: {current_user_id}')
    
    user = User.query.get(current_user_id)
    if not user:
        current_app.logger.error(f'用户不存在: {current_user_id}')
        return jsonify({'error': 'User not found'}), 404

    if 'avatar' not in request.files:
        current_app.logger.error('请求中没有avatar文件')
        return jsonify({'error': 'No avatar file provided'}), 400

    file = request.files['avatar']
    current_app.logger.info(f'原始文件名: {file.filename}')
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' not in file.filename:
        current_app.logger.error(f'文件没有扩展名: {file.filename}')
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
    
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    current_app.logger.info(f'文件扩展名: {file_ext}')
    
    if file_ext not in allowed_extensions:
        current_app.logger.error(f'不支持的文件类型: {file_ext}')
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400

    # 检查文件大小 (最大 5MB)
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    current_app.logger.info(f'文件大小: {file_size} bytes')
    
    max_size = 5 * 1024 * 1024  # 5MB
    if file_size > max_size:
        current_app.logger.error(f'文件太大: {file_size} > {max_size}')
        return jsonify({'error': 'File too large. Maximum size is 5MB'}), 400

    # 生成唯一文件名 - 使用时间戳避免中文和空格问题
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{uuid.uuid4().hex}.{file_ext}"
    current_app.logger.info(f'生成的文件名: {unique_filename}')
    
    # 保存文件到 avatars 子目录
    upload_dir = os.path.join(current_app.config['USER_UPLOADS_DIR'], 'avatars')
    current_app.logger.info(f'上传目录: {upload_dir}')
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    current_app.logger.info(f'完整文件路径: {file_path}')
    file.save(file_path)
    current_app.logger.info(f'文件保存成功')
    
    # 验证文件是否存在
    if os.path.exists(file_path):
        current_app.logger.info(f'文件验证成功: {file_path}')
    else:
        current_app.logger.error(f'文件验证失败: {file_path}')
    
    # 生成访问URL
    avatar_url = f"/uploads/avatars/{unique_filename}"
    current_app.logger.info(f'生成的avatar_url: {avatar_url}')
    
    user.avatar_url = avatar_url
    db.session.commit()
    current_app.logger.info(f'数据库更新成功,用户avatar_url: {user.avatar_url}')
    
    current_app.logger.info('=== 头像上传完成 ===')

    return jsonify({
        'message': 'Avatar uploaded successfully',
        'avatar_url': avatar_url,
        'user': user.to_dict()
    }), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard token)"""
    return jsonify({'message': 'Logged out successfully'}), 200
