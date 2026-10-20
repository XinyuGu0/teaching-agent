import os
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from app.config import config
from app.extensions import init_extensions, db

def create_app(config_name='default', test_config=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    if test_config is not None:
        app.config.update(test_config)

    # Ensure data directories exist
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['KNOWLEDGE_BASE_DIR'], exist_ok=True)
    os.makedirs(app.config['USER_UPLOADS_DIR'], exist_ok=True)
    os.makedirs(os.path.join(app.config['USER_UPLOADS_DIR'], 'avatars'), exist_ok=True)
    os.makedirs(app.config['VECTOR_DB_DIR'], exist_ok=True)
    os.makedirs(app.config['GENERATED_PPTS_DIR'], exist_ok=True)
    os.makedirs(app.config['GENERATED_LESSONS_DIR'], exist_ok=True)
    os.makedirs(app.config['TEMPLATES_DIR'], exist_ok=True)

    # Configure CORS first, before initializing extensions
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": app.config['CORS_ORIGINS'],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             },
             r"/uploads/*": {
                 "origins": app.config['CORS_ORIGINS'],
                 "methods": ["GET", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         },
         expose_headers=["Content-Type", "Authorization"])
    
    # 在任何路由处理之前拦截OPTIONS请求，避免重定向
    @app.before_request
    def handle_options_request():
        if request.method == 'OPTIONS':
            # 直接返回204，不进行任何路由匹配
            response = app.make_default_options_response()
            # 确保CORS头正确设置
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
    
    # Initialize extensions
    init_extensions(app)

    # Set slash handling before routes are registered.
    app.url_map.strict_slashes = False

    # Register blueprints
    from app.api import auth, conversation, document, template, ppt, lesson_plan, digital_human, share
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(conversation.bp, url_prefix='/api/conversations')
    app.register_blueprint(document.bp, url_prefix='/api/documents')
    app.register_blueprint(template.bp, url_prefix='/api/templates')
    app.register_blueprint(ppt.bp, url_prefix='/api/ppts')
    app.register_blueprint(lesson_plan.bp, url_prefix='/api/lesson-plans')
    app.register_blueprint(digital_human.bp, url_prefix='/api/digital-human')
    app.register_blueprint(share.bp, url_prefix='/api/shares')
    

    # 在路由注册后添加OPTIONS处理器，确保它在所有API路径上都有效
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    @app.route('/api/<path:path>/', methods=['OPTIONS'])
    def handle_options(path=None):
        """全局OPTIONS处理器，避免重定向"""
        return '', 204

    # 静态文件服务 - 提供上传文件的访问
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """提供上传文件的访问"""
        upload_dir = app.config['USER_UPLOADS_DIR']
        return send_from_directory(upload_dir, filename)

    # Register WebSocket handlers
    from app.websocket import chat
    chat.register_handlers()

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
