
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

print("=" * 60)
print("最终CORS测试")
print("=" * 60)

# 测试OPTIONS请求到/api/templates
url = "http://localhost:5000/api/templates"
headers = {
    'Origin': 'http://localhost:5173',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'content-type, authorization'
}

print(f"\n发送OPTIONS请求到: {url}")
response = requests.options(url, headers=headers)

print(f"\n状态码: {response.status_code}")

if response.status_code == 204:
    print("✓ 成功！OPTIONS请求返回204，没有重定向")
    print("\n响应头:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
elif response.status_code == 308:
    print("✗ 仍然有重定向！状态码: 308")
    if 'Location' in response.headers:
        print(f"  重定向到: {response.headers['Location']}")
else:
    print(f"✗ 意外的状态码: {response.status_code}")

print("\n" + "=" * 60)
print("如果状态码是204，说明修复成功！")
print("请刷新浏览器（Ctrl+F5）并测试上传功能。")
print("=" * 60)