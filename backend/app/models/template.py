import uuid
from datetime import datetime
from app.extensions import db

class Template(db.Model):
    """Template model"""
    __tablename__ = 'templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)  # NULL for built-in
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True, index=True)  # 模板分类：business, education, creative, minimal, etc.
    template_type = db.Column(db.String(20), nullable=False)  # builtin, uploaded, online
    file_path = db.Column(db.String(500), nullable=False)
    thumbnail_path = db.Column(db.String(500), nullable=True)
    source_url = db.Column(db.String(500), nullable=True)  # For online templates
    source_format = db.Column(db.String(20), nullable=True)  # 原始上传格式
    is_public = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    styles = db.Column(db.JSON, nullable=True)  # 存储解析后的模板样式（背景色、字体、布局等）
    template_info = db.Column(db.JSON, nullable=True)  # 模板基本信息（页面分布等）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ppts = db.relationship('PPT', backref='template', lazy='dynamic')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'template_type': self.template_type,
            'file_path': self.file_path,
            'thumbnail_path': self.thumbnail_path,
            'source_url': self.source_url,
            'source_format': self.source_format,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'styles': self.styles,
            'template_info': self.template_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Template {self.name}>'