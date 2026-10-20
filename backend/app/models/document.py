import uuid
from datetime import datetime, timezone
from app.extensions import db

class Document(db.Model):
    """Document model"""
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, docx, pptx, xlsx, image, video
    file_size = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='processing')  # processing, ready, failed
    is_knowledge_base = db.Column(db.Boolean, default=False)
    vector_ids = db.Column(db.JSON, default=list)  # Store vector DB IDs
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_path': self.file_path,
            'status': self.status,
            'is_knowledge_base': self.is_knowledge_base,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

    def __repr__(self):
        return f'<Document {self.original_filename}>'
