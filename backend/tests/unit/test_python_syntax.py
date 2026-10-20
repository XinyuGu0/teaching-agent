import ast
from pathlib import Path

def test_application_and_migrations_parse():
    backend = Path(__file__).resolve().parents[2]
    for directory in (backend / "app", backend / "migrations"):
        for source in directory.rglob("*.py"):
            ast.parse(source.read_text(encoding="utf-8-sig"), filename=str(source))
