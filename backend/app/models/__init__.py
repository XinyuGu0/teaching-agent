# Import all models for Flask-Migrate
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.document import Document
from app.models.template import Template
from app.models.ppt import PPT, LessonPlan
from app.models.share import ConversationShare

__all__ = ['User', 'Conversation', 'Message', 'Document', 'Template', 'PPT', 'LessonPlan', 'ConversationShare']
