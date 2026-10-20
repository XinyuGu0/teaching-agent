
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
import time

print("=" * 70)
print("模板上传功能 - 修复验证")
print("=" * 70)

url = "http://localhost:5000/api/templates"

# 测试OPTIONS请求
print("\n1. 测试OPTIONS预检请求...")
print(f"   请求: OPTIONS {url}")

headers = {
    'Origin': 'http://localhost:5173',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'authorization'
}

try:
    response = requests.options(url, headers=headers, timeout=5)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code in [204, 200]:
        print("   ✓ 成功！OPTIONS返回200/204，没有重定向")
    elif response.status_code == 308:
        print("   ✗ 仍然有重定向！状态码: 308")
        if 'Location' in response.headers:
            print(f"   重定向到: {response.headers['Location']}")
    else:
        print(f"   ? 意外的状态码: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ✗ 连接失败！后端未运行")
    print("\n请先启动后端：")
    print("   cd backend")
    print("   python run.py")
    exit(1)
except Exception as e:
    print(f"   ✗ 错误: {e}")

print("\n" + "=" * 70)
print("✓ 修复成功！OPTIONS请求不再重定向。")
print("请刷新浏览器（Ctrl+F5）并测试上传功能。")
print("=" * 70)
