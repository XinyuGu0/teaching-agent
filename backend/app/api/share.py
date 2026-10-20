import uuid
import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.share import ConversationShare

bp = Blueprint('share', __name__)


@bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by username or email for sharing"""
    current_user_id = get_jwt_identity()
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 1:
        return jsonify({'users': []}), 200
    
    users = User.query.filter(
        User.id != current_user_id,
        db.or_(
            User.username.ilike(f'%{query}%'),
            User.email.ilike(f'%{query}%'),
            User.nickname.ilike(f'%{query}%')
        )
    ).limit(20).all()
    
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'nickname': u.nickname,
            'avatar_url': u.avatar_url,
            'email': u.email
        } for u in users]
    }), 200


@bp.route('/<conversation_id>/share', methods=['GET'])
@jwt_required()
def get_share_settings(conversation_id):
    """Get share settings for a conversation"""
    current_user_id = get_jwt_identity()
    
    conversation = Conversation.query.filter_by(
        id=conversation_id, user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
    
    share = ConversationShare.query.filter_by(
        conversation_id=conversation_id,
        is_active=True
    ).first()
    
    if not share:
        return jsonify({
            'share_type': 'disabled',
            'share_token': None,
            'password': None,
            'allowed_users': [],
            'share_link': None
        }), 200
    
    # Get allowed user details
    allowed_user_details = []
    if share.allowed_user_ids:
        for uid in share.allowed_user_ids:
            user = User.query.get(uid)
            if user:
                allowed_user_details.append({
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                    'avatar_url': user.avatar_url,
                    'email': user.email
                })
    
    # Build share link
    frontend_base = request.headers.get('Origin', request.host_url.rstrip('/'))
    share_link = f"{frontend_base}/share-cop/{share.share_token}" if share.share_token else None
    
    return jsonify({
        'share_type': share.share_type,
        'share_token': share.share_token,
        'password': share.password,
        'allowed_users': allowed_user_details,
        'share_link': share_link,
        'created_at': share.created_at.isoformat() if share.created_at else None
    }), 200


@bp.route('/<conversation_id>/share', methods=['POST'])
@jwt_required()
def update_share_settings(conversation_id):
    """Create or update share settings for a conversation"""
    current_user_id = get_jwt_identity()
    
    conversation = Conversation.query.filter_by(
        id=conversation_id, user_id=current_user_id
    ).first()
    
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
    
    data = request.get_json() or {}
    share_type = data.get('share_type', 'disabled')  # disabled, internal, public
    password = data.get('password', None)
    allowed_user_ids = data.get('allowed_user_ids', [])
    
    # Validate share_type
    if share_type not in ('disabled', 'internal', 'public', 'collaborate'):
        return jsonify({'error': '无效的分享类型'}), 400
    
    # Find or create share record
    share = ConversationShare.query.filter_by(
        conversation_id=conversation_id
    ).first()
    
    if share_type == 'disabled':
        # Disable sharing
        if share:
            share.is_active = False
            share.share_type = 'disabled'
            share.share_token = None
            share.password = None
            share.allowed_user_ids = []
        db.session.commit()
        return jsonify({'message': '分享已关闭', 'share_type': 'disabled'}), 200
    
    if not share:
        share = ConversationShare(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            created_by=current_user_id,
            share_token=secrets.token_urlsafe(16)
        )
        db.session.add(share)
    
    share.share_type = share_type
    share.is_active = True
    
    # Generate token if not exists
    if not share.share_token:
        share.share_token = secrets.token_urlsafe(16)
    
    # Handle internal sharing
    if share_type == 'internal':
        if not allowed_user_ids:
            return jsonify({'error': '请选择至少一位用户'}), 400
        # Validate user IDs
        valid_ids = []
        for uid in allowed_user_ids:
            if User.query.get(uid):
                valid_ids.append(uid)
        share.allowed_user_ids = valid_ids
        share.password = None
    
    # Handle public sharing
    elif share_type == 'public':
        share.password = password if password else None
        share.allowed_user_ids = []

    # Handle collaborate sharing (like public but with collab intent)
    elif share_type == 'collaborate':
        share.password = password if password else None
        share.allowed_user_ids = []
    
    db.session.commit()
    
    # Build share link
    frontend_base = request.headers.get('Origin', request.host_url.rstrip('/'))
    share_link = f"{frontend_base}/share-cop/{share.share_token}"
    
    # Get allowed user details
    allowed_user_details = []
    if share.allowed_user_ids:
        for uid in share.allowed_user_ids:
            user = User.query.get(uid)
            if user:
                allowed_user_details.append({
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname,
                    'avatar_url': user.avatar_url,
                    'email': user.email
                })
    
    return jsonify({
        'message': '分享设置已更新',
        'share_type': share.share_type,
        'share_token': share.share_token,
        'password': share.password,
        'allowed_users': allowed_user_details,
        'share_link': share_link
    }), 200


@bp.route('/access/<token>', methods=['GET'])
def access_shared_conversation(token):
    """Access a shared conversation by token (public endpoint)"""
    share = ConversationShare.query.filter_by(
        share_token=token,
        is_active=True
    ).first()
    
    if not share:
        return jsonify({'error': '分享链接无效或已失效'}), 404
    
    # Check if password required
    password_required = share.password is not None and share.password != ''
    
    conversation = Conversation.query.get(share.conversation_id)
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
    
    # Return basic info (password verification done separately)
    result = {
        'conversation_id': conversation.id,
        'title': conversation.title,
        'share_type': share.share_type,
        'password_required': password_required,
        'owner': None
    }
    
    # Get owner info
    owner = User.query.get(conversation.user_id)
    if owner:
        result['owner'] = {
            'nickname': owner.nickname or owner.username,
            'avatar_url': owner.avatar_url
        }
    
    return jsonify(result), 200


@bp.route('/access/<token>/verify', methods=['POST'])
def verify_shared_access(token):
    """Verify password for a shared conversation and return messages"""
    share = ConversationShare.query.filter_by(
        share_token=token,
        is_active=True
    ).first()
    
    if not share:
        return jsonify({'error': '分享链接无效或已失效'}), 404
    
    data = request.get_json() or {}
    
    # Check password if required
    if share.password:
        provided_password = data.get('password', '')
        if provided_password != share.password:
            return jsonify({'error': '密码错误'}), 403
    
    # For internal shares, verify user
    if share.share_type == 'internal':
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '需要登录才能访问'}), 401
        
        try:
            from flask_jwt_extended import decode_token
            token_str = auth_header.split(' ', 1)[1]
            decoded = decode_token(token_str)
            user_id = decoded['sub']
            if user_id not in (share.allowed_user_ids or []):
                return jsonify({'error': '您没有权限访问此对话'}), 403
        except Exception:
            return jsonify({'error': '认证失败'}), 401
    
    # Return conversation with messages
    conversation = Conversation.query.get(share.conversation_id)
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
    
    messages = Message.query.filter_by(
        conversation_id=conversation.id
    ).order_by(Message.created_at.asc()).all()
    
    owner = User.query.get(conversation.user_id)
    
    return jsonify({
        'conversation': {
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat() if conversation.created_at else None
        },
        'owner': {
            'user_id': owner.id if owner else None,
            'nickname': owner.nickname or owner.username if owner else '未知用户',
            'avatar_url': owner.avatar_url if owner else None
        },
        'messages': [msg.to_dict() for msg in messages]
    }), 200