import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    teacher_gender = db.Column(db.String(20), nullable=True)
    teacher_age = db.Column(db.Integer, nullable=True)
    school_name = db.Column(db.String(200), nullable=True)
    subject_category = db.Column(db.String(100), nullable=True)
    courses = db.Column(db.JSON, nullable=True)
    teaching_styles = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    templates = db.relationship('Template', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ppts = db.relationship('PPT', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    lesson_plans = db.relationship('LessonPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'email': self.email,
            'teacher_gender': self.teacher_gender,
            'teacher_age': self.teacher_age,
            'school_name': self.school_name,
            'subject_category': self.subject_category,
            'courses': self.courses or [],
            'teaching_styles': self.teaching_styles or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
