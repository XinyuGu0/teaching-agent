# API blueprints
from app.api import auth
from app.api import conversation
from app.api import document
from app.api import template
from app.api import ppt
from app.api import lesson_plan

# 为所有blueprint设置strict_slashes=False以避免重定向
auth.bp.strict_slashes = False
conversation.bp.strict_slashes = False
document.bp.strict_slashes = False
template.bp.strict_slashes = False
ppt.bp.strict_slashes = False
lesson_plan.bp.strict_slashes = False

__all__ = ['auth', 'conversation', 'document', 'template', 'ppt', 'lesson_plan']
