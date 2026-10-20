#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
exec "$PYTHON" backend/run.py
