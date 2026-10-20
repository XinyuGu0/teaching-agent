import uuid
from datetime import datetime
from app.extensions import db

class PPT(db.Model):
    """PPT model"""
    __tablename__ = 'ppts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    template_id = db.Column(db.String(36), db.ForeignKey('templates.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    theme = db.Column(db.String(50), default='modern')  # 主题：modern, business, academic, creative
    outline = db.Column(db.JSON, default=dict)  # Store structured outline
    slides_data = db.Column(db.JSON, default=list)  # Store slides data for web rendering
    file_path = db.Column(db.String(500), nullable=True)
    version = db.Column(db.Integer, default=1)  # Track refinement versions
    status = db.Column(db.String(20), default='generating')  # generating, ready, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'title': self.title,
            'theme': self.theme,
            'outline': self.outline,
            'slides_data': self.slides_data,  # 保持一致，使用slides_data
            'file_path': self.file_path,
            'pptx_url': f'/api/ppt/{self.id}/download' if self.file_path else None,
            'version': self.version,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<PPT {self.title}>'


class LessonPlan(db.Model):
    """Lesson Plan model"""
    __tablename__ = 'lesson_plans'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False, index=True)
    ppt_id = db.Column(db.String(36), db.ForeignKey('ppts.id'), nullable=True, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='generating')  # generating, ready, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'ppt_id': self.ppt_id,
            'user_id': self.user_id,
            'title': self.title,
            'file_path': self.file_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<LessonPlan {self.title}>'
