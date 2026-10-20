import uuid
from datetime import datetime, timezone
from app.extensions import db

class Conversation(db.Model):
    """Conversation model"""
    __tablename__ = 'conversations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, default='New Conversation')
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    state = db.Column(db.String(50), default='INITIAL')  # Conversation state for guidance
    requirements = db.Column(db.JSON, default=dict)  # Collected requirements
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan', order_by='Message.created_at')
    ppts = db.relationship('PPT', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    lesson_plans = db.relationship('LessonPlan', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_messages=False):
        """Convert to dictionary"""
        # Add timezone info if not present
        created_at = self.created_at
        updated_at = self.updated_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if updated_at and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'status': self.status,
            'state': self.state,
            'requirements': self.requirements,
            'created_at': created_at.isoformat() if created_at else None,
            'updated_at': updated_at.isoformat() if updated_at else None
        }
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        return data

    def __repr__(self):
        return f'<Conversation {self.id}>'


class Message(db.Model):
    """Message model"""
    __tablename__ = 'messages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    meta_data = db.Column(db.JSON, default=dict)  # Store outline, state, etc.
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # Who sent this message (for collab)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert to dictionary"""
        # Add timezone info if not present
        created_at = self.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        meta = self.meta_data or {}
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'thinkingContent': meta.get('thinking_content', ''),
            'meta_data': meta,
            'user_id': self.user_id,
            'created_at': created_at.isoformat() if created_at else None
        }

    def __repr__(self):
        return f'<Message {self.id}>'
