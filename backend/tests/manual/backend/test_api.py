
# Historical manual test: never collected as an automatic test.
import os as _os
import sys as _sys
from pathlib import Path as _Path
if __name__ != "__main__":
    import unittest as _unittest
    raise _unittest.SkipTest("Historical manual test; run explicitly after reviewing it")
if _os.getenv("RUN_MANUAL_TESTS") != "1":
    raise SystemExit("Review this script first; set RUN_MANUAL_TESTS=1 to allow external calls and writes")
_backend = next(parent for parent in _Path(__file__).resolve().parents if (parent / "app/config.py").is_file())
_sys.path.insert(0, str(_backend))
from dotenv import load_dotenv as _load_dotenv
_load_dotenv(_backend / ".env")

import requests
try:
    response = requests.get('http://localhost:5000/api/templates', timeout=10)
    print(f'API响应状态: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'找到 {len(data)} 个模板')
        for t in data[:3]:
            print(f'- {t["name"]} ({t["id"]})')
    else:
        print(f'API错误: {response.text}')
except Exception as e:
    print(f'连接失败: {e}')