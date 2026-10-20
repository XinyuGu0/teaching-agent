"""
测试BuildSh生成器功能
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

import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from app.services.build_sh_generator import get_build_sh_generator

def test_get_available_templates():
    """测试获取可用模板"""
    print("\n========== 测试1: 获取可用模板 ==========")
    
    generator = get_build_sh_generator()
    templates = generator.get_available_templates()
    
    print(f"找到 {len(templates)} 个可用模板:")
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['name']} (ID: {template['id']})")
        print(f"   目录: {template['dir_name']}")
        print(f"   文件: {template['file_name']}")
        print(f"   背景色: #{template['background_color']}")
        print()


def test_read_build_sh():
    """测试读取build.sh文件"""
    print("\n========== 测试2: 读取build.sh文件 ==========")
    
    generator = get_build_sh_generator()
    
    # 测试读取第一个模板的build.sh
    templates = generator.get_available_templates()
    if templates:
        template_id = templates[0]['id']
        print(f"读取模板: {template_id}")
        
        try:
            content = generator.read_build_sh(template_id)
            print(f"成功读取build.sh，长度: {len(content)} 字节")
            print(f"前100个字符: {content[:100]}...")
        except Exception as e:
            print(f"读取失败: {e}")


def test_generate_simple_ppt():
    """测试生成简单PPT（不调用LLM，只测试结构）"""
    print("\n========== 测试3: 测试大纲结构 ==========")
    
    # 创建测试大纲
    outline = {
        "title": "人工智能的未来",
        "slides": [
            {
                "slide_number": 1,
                "title": "核心技术",
                "content_points": ["机器学习", "深度学习", "自然语言处理"],
                "layout": "pillars"
            },
            {
                "slide_number": 2,
                "title": "应用数据",
                "content_points": ["100万用户", "增长率200%"],
                "layout": "evidence"
            }
        ]
    }
    
    print("测试大纲:")
    print(f"  主题: {outline['title']}")
    print(f"  内页数: {len(outline['slides'])}")
    print(f"  总页数: {2 + len(outline['slides'])} (封面 + {len(outline['slides'])}内页 + 结尾)")
    
    for i, slide in enumerate(outline['slides'], 1):
        print(f"\n  第{i+1}页:")
        print(f"    标题: {slide['title']}")
        print(f"    要点: {', '.join(slide['content_points'])}")
        print(f"    布局: {slide['layout']}")


if __name__ == '__main__':
    print("=" * 60)
    print("BuildSh生成器功能测试")
    print("=" * 60)
    
    try:
        test_get_available_templates()
        test_read_build_sh()
        test_generate_simple_ppt()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
