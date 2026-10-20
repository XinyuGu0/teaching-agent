"""
测试BuildSh生成器
验证从build.sh到PPT生成的完整流程
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

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.build_sh_generator import get_build_sh_generator
from app.services.build_sh_templates import get_all_template_ids, get_template_metadata

def test_list_templates():
    """测试列出所有可用模板"""
    print("=" * 60)
    print("测试1: 列出所有可用模板")
    print("=" * 60)
    
    generator = get_build_sh_generator()
    templates = generator.get_available_templates()
    
    print(f"\n找到 {len(templates)} 个可用模板:\n")
    for template in templates:
        print(f"  ID: {template['id']}")
        print(f"  名称: {template['name']}")
        print(f"  分类: {template['category']}")
        print(f"  标签: {', '.join(template['tags'])}")
        print(f"  描述: {template['description']}")
        print()

def test_read_build_sh():
    """测试读取build.sh内容"""
    print("=" * 60)
    print("测试2: 读取build.sh内容")
    print("=" * 60)
    
    generator = get_build_sh_generator()
    
    # 测试读取第一个模板
    template_id = 'builtin_science--time-travel'
    print(f"\n读取模板: {template_id}")
    
    try:
        build_sh = generator.read_build_sh(template_id)
        print(f"✅ 成功读取 build.sh，长度: {len(build_sh)} 字节")
        print(f"\n前200字符预览:")
        print(build_sh[:200])
    except Exception as e:
        print(f"❌ 读取失败: {e}")

def test_generate_prompt():
    """测试生成LLM提示词"""
    print("\n" + "=" * 60)
    print("测试3: 生成LLM提示词")
    print("=" * 60)
    
    generator = get_build_sh_generator()
    
    # 准备测试大纲
    outline = {
        'title': '人工智能的未来',
        'slides': [
            {
                'slide_number': 1,
                'title': '核心技术',
                'content_points': ['机器学习', '深度学习', '自然语言处理'],
                'layout': 'pillars'
            },
            {
                'slide_number': 2,
                'title': '应用数据',
                'content_points': ['100万用户', '增长率200%'],
                'layout': 'evidence'
            }
        ]
    }
    
    template_id = 'builtin_science--time-travel'
    output_path = 'test_output.pptx'
    
    print(f"\n模板ID: {template_id}")
    print(f"大纲主题: {outline['title']}")
    print(f"内页数量: {len(outline['slides'])}")
    print(f"总页数: {2 + len(outline['slides'])} (封面 + {len(outline['slides'])}内页 + 结尾)")
    
    try:
        # 读取build.sh
        build_sh = generator.read_build_sh(template_id)
        
        # 生成提示词（不实际调用LLM）
        total_pages = 2 + len(outline['slides'])
        prompt = generator._build_prompt(build_sh, outline, output_path, total_pages)
        
        print(f"\n✅ 成功生成提示词，长度: {len(prompt)} 字符")
        
        # 检查关键内容
        if '人工智能的未来' in prompt:
            print("✅ 提示词包含大纲主题")
        if 'science--time-travel' in prompt or 'Time_Travel' in prompt:
            print("✅ 提示词包含模板信息")
        if '共4页' in prompt:
            print("✅ 提示词包含正确的页数信息")
        
        # 显示提示词前500字符
        print(f"\n提示词预览（前500字符）:")
        print(prompt[:500])
        
    except Exception as e:
        print(f"❌ 生成提示词失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """运行所有测试"""
    print("\n" + "🚀 " * 20)
    print("BuildSh生成器测试")
    print("🚀 " * 20 + "\n")
    
    try:
        test_list_templates()
        test_read_build_sh()
        test_generate_prompt()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        print("\n下一步:")
        print("1. 启动后端服务: python run.py")
        print("2. 通过前端选择内置模板生成PPT")
        print("3. 查看日志确认LLM生成的Python代码")
        print("4. 验证生成的PPT文件")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
