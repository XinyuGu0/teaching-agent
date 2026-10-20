
# Historical data-maintenance script. Review paths and back up data before use.
import os as _os
import sys as _sys
from pathlib import Path as _Path
if __name__ != "__main__" or _os.getenv("ALLOW_LEGACY_MAINTENANCE") != "1":
    raise SystemExit("Historical maintenance is disabled; review paths and back up data before setting ALLOW_LEGACY_MAINTENANCE=1")
_backend = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_backend))
from dotenv import load_dotenv as _load_dotenv
_load_dotenv(_backend / ".env")

from app.extensions import db
from app import create_app
from app.models.conversation import Message
from datetime import datetime, timezone

app = create_app()

with app.app_context():
    msgs = Message.query.order_by(Message.created_at.desc()).limit(3).all()

    if msgs:
        print("Latest messages:")
        for msg in msgs:
            print(f"  ID: {msg.id}")
            print(f"  Created: {msg.created_at}")
            print(f"  ISO: {msg.created_at.isoformat()}")
            print(f"  Now UTC: {datetime.now(timezone.utc)}")
            print()
    else:
        print("No messages found")
