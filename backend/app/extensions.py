from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO()
migrate = Migrate()
ma = Marshmallow()
celery = Celery()

def init_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    # CORS已在app初始化时配置，这里不再重复初始化
    # cors.init_app(app, ...) 
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'])
    migrate.init_app(app, db)
    ma.init_app(app)

    # Configure Celery
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    celery.Task = _make_celery_task(app)

    return app

def _make_celery_task(app):
    """Create Celery task class with Flask app context"""
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    return ContextTask
