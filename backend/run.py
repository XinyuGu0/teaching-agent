"""Local development entry point: python backend/run.py."""
import logging
import os
from app import create_app
from app.extensions import socketio

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    socketio.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true"},
        allow_unsafe_werkzeug=True,
    )
