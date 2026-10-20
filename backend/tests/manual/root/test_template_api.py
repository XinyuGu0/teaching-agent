
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
import json

# 测试配置
BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = _os.environ["TEST_PASSWORD"]

def test_template_api():
    """测试模板API"""
    print("=" * 60)
    print("测试模板API")
    print("=" * 60)
    
    # 1. 注册用户（如果不存在）
    print("\n1. 注册用户...")
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "username": USERNAME,
            "email": "admin@test.com",
            "password": PASSWORD
        }
    )
    
    if register_response.status_code in [200, 201]:
        print(f"✓ 注册成功")
    elif register_response.status_code == 400 and "already exists" in register_response.text:
        print(f"✓ 用户已存在")
    else:
        print(f"注册失败: {register_response.status_code}")
        print(register_response.text)
    
    # 2. 登录获取token
    print("\n2. 登录...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()['access_token']
    print(f"✓ 登录成功，获取token")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 3. 测试获取模板列表
    print("\n3. 获取模板列表...")
    templates_response = requests.get(
        f"{BASE_URL}/api/templates",
        headers=headers
    )
    
    if templates_response.status_code == 200:
        data = templates_response.json()
        print(f"✓ 获取成功，共 {len(data['templates'])} 个模板")
    else:
        print(f"✗ 获取失败: {templates_response.status_code}")
        print(templates_response.text)
    
    # 4. 测试获取分类
    print("\n4. 获取模板分类...")
    categories_response = requests.get(
        f"{BASE_URL}/api/templates/categories",
        headers=headers
    )
    
    if categories_response.status_code == 200:
        categories = categories_response.json()
        print(f"✓ 获取成功，共 {len(categories)} 个分类")
    else:
        print(f"✗ 获取失败: {categories_response.status_code}")
        print(categories_response.text)
    
    # 5. 测试上传模板
    print("\n5. 测试上传模板...")
    
    # 创建一个假的PPT文件用于测试
    test_file_path = "test_template.pptx"
    with open(test_file_path, 'wb') as f:
        f.write(b'This is a test PPT file')
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
            data = {
                'name': '测试模板',
                'description': '这是一个测试模板',
                'category': 'other'
            }
            
            upload_response = requests.post(
                f"{BASE_URL}/api/templates",
                headers=headers,
                files=files,
                data=data
            )
            
            if upload_response.status_code in [200, 201]:
                print(f"✓ 上传成功")
                print(json.dumps(upload_response.json(), indent=2, ensure_ascii=False))
            else:
                print(f"✗ 上传失败: {upload_response.status_code}")
                print(upload_response.text)
    finally:
        # 清理测试文件
        import os
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_template_api()