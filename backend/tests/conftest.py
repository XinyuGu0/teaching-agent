import pytest
from app import create_app
from app.extensions import db

@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    import socket
    def blocked(*args, **kwargs):
        raise AssertionError("Automatic tests must not open network connections")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)

@pytest.fixture
def app(tmp_path):
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-only-secret-not-for-deployment",
        "JWT_SECRET_KEY": "test-only-jwt-secret-not-for-deployment",
    }
    for key in ("DATA_DIR", "KNOWLEDGE_BASE_DIR", "USER_UPLOADS_DIR", "VECTOR_DB_DIR", "GENERATED_PPTS_DIR", "GENERATED_LESSONS_DIR", "TEMPLATES_DIR"):
        config[key] = str(tmp_path / key.lower())
    config["UPLOAD_FOLDER"] = config["DATA_DIR"]
    app = create_app(test_config=config)
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

@pytest.fixture
def client(app):
    return app.test_client()
