import uuid
from datetime import datetime, timezone
from app.extensions import db


class ConversationShare(db.Model):
    """Conversation sharing model"""
    __tablename__ = 'conversation_shares'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False, index=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    share_type = db.Column(db.String(20), default='disabled')  # disabled, internal, public
    share_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    password = db.Column(db.String(50), nullable=True)  # Optional password for public shares
    allowed_user_ids = db.Column(db.JSON, default=list)  # List of user IDs for internal shares
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    conversation = db.relationship('Conversation', backref=db.backref('shares', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'created_by': self.created_by,
            'share_type': self.share_type,
            'share_token': self.share_token,
            'password': self.password,
            'allowed_user_ids': self.allowed_user_ids or [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<ConversationShare {self.id}>'
