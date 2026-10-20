"""
测试BuildShPPTGenerator功能
"""

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

import os
import sys
import json

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.build_sh_generator import get_build_sh_generator

def test_get_available_templates():
    """测试获取可用模板"""
    print("=" * 60)
    print("测试1: 获取可用模板")
    print("=" * 60)
    
    generator = get_build_sh_generator()
    templates = generator.get_available_templates()
    
    print(f"\n找到 {len(templates)} 个可用模板:\n")
    
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['name']}")
        print(f"   ID: {template['id']}")
        print(f"   目录: {template['dir_name']}")
        print(f"   文件: {template['file_name']}")
        print(f"   字体: {template['font']}")
        print()
    
    return templates


def test_read_build_sh():
    """测试读取build.sh文件"""
    print("=" * 60)
    print("测试2: 读取build.sh文件")
    print("=" * 60)
    
    generator = get_build_sh_generator()
    
    # 测试读取第一个模板的build.sh
    template_id = 'builtin_science--time-travel'
    
    try:
        content = generator.read_build_sh(template_id)
        print(f"\n成功读取 {template_id} 的 build.sh")
        print(f"文件大小: {len(content)} 字节")
        print(f"\n前500字符预览:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)
        return True
    except Exception as e:
        print(f"\n❌ 读取失败: {e}")
        return False


def test_generate_simple_ppt():
    """测试生成简单的3页PPT"""
    print("\n" + "=" * 60)
    print("测试3: 生成3页PPT（封面+1内页+结尾）")
    print("=" * 60)
    
    generator = get_build_sh_generator()
    
    # 准备测试大纲
    outline = {
        "title": "人工智能的未来",
        "slides": [
            {
                "slide_number": 1,
                "title": "核心技术",
                "content_points": ["机器学习", "深度学习", "自然语言处理"],
                "layout": "pillars"
            }
        ]
    }
    
    # 输出路径
    output_path = os.path.join(os.path.dirname(__file__), 'test_output', 'test_3pages.pptx')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 进度回调
    def progress_callback(info):
        print(f"  进度: {info['progress']}% - {info['message']}")
    
    try:
        print(f"\n开始生成PPT...")
        print(f"模板: builtin_science--time-travel")
        print(f"大纲: {json.dumps(outline, ensure_ascii=False, indent=2)}")
        print(f"输出: {output_path}\n")
        
        result = generator.generate_with_llm(
            template_id='builtin_science--time-travel',
            outline=outline,
            output_path=output_path,
            progress_callback=progress_callback
        )
        
        if result['success']:
            print(f"\n✅ PPT生成成功!")
            print(f"   文件路径: {result['file_path']}")
            print(f"   总页数: {result['total_pages']}")
            
            # 检查文件是否存在
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   文件大小: {file_size} 字节")
            
            # 显示生成的Python代码（前1000字符）
            if 'python_code' in result:
                print(f"\n生成的Python代码预览（前1000字符）:")
                print("-" * 60)
                print(result['python_code'][:1000])
                print("-" * 60)
            
            return True
        else:
            print(f"\n❌ PPT生成失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🚀 " * 20)
    print("BuildShPPTGenerator 功能测试")
    print("🚀 " * 20 + "\n")
    
    results = []
    
    # 测试1: 获取可用模板
    templates = test_get_available_templates()
    results.append(("获取可用模板", len(templates) > 0))
    
    # 测试2: 读取build.sh
    results.append(("读取build.sh", test_read_build_sh()))
    
    # 测试3: 生成3页PPT
    results.append(("生成3页PPT", test_generate_simple_ppt()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")


if __name__ == '__main__':
    main()
