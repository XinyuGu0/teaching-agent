
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

def test_cors_with_origin(origin):
    """测试特定origin的CORS请求"""
    url = "http://localhost:5000/api/templates"
    
    # 发送OPTIONS请求，模拟浏览器
    headers = {
        'Origin': origin,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'authorization'
    }
    
    response = requests.options(url, headers=headers)
    
    print(f"\n测试Origin: {origin}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
        
        if response.headers.get('Access-Control-Allow-Origin') == origin:
            print("✓ CORS配置正确")
        else:
            print("✗ CORS配置不匹配")
    else:
        print(f"✗ 请求失败")
    
    return response.status_code

print("=" * 60)
print("CORS预检请求测试")
print("=" * 60)

# 测试localhost
test_cors_with_origin('http://localhost:5173')

# 测试127.0.0.1
test_cors_with_origin('http://127.0.0.1:5173')

print("\n" + "=" * 60)
print("请确保后端已重启以使配置生效！")
print("=" * 60)
