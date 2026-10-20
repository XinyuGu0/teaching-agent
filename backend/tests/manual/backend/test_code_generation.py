
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

from app.services.build_sh_generator import BuildShPPTGenerator
import json
import os

# 测试代码生成（不执行OfficeCLI命令）
generator = BuildShPPTGenerator()

# 简单的测试大纲
outline = {
    'title': '测试PPT',
    'slides': [
        {'title': '第一页', 'content': '这是第一页内容'}
    ]
}

def progress_callback(progress_data):
    print(f"进度: {progress_data.get('progress', 0)}% - {progress_data.get('message', '')}")

try:
    # 只测试到代码生成阶段
    template_id = 'builtin_builtin_brand--aura-coffee'
    output_path = 'test_output.pptx'

    # 读取build.sh
    build_sh_content = generator.read_build_sh(template_id)
    print("成功读取build.sh模板")

    # 分析大纲
    slides = outline.get('slides', [])
    total_pages = 2 + len(slides)
    print(f"总页数: {total_pages}")

    # 构建提示词
    prompt = generator._build_prompt(build_sh_content, outline, output_path, total_pages)
    print("成功构建LLM提示词")

    # 调用LLM
    print("正在调用LLM...")
    response = generator._call_llm(prompt, enable_thinking=True)
    print("LLM调用成功")

    # 解析响应
    python_code = generator._parse_llm_response(response)
    print("成功解析LLM响应")

    # 验证代码
    generator._validate_generated_code(python_code)
    print("代码验证通过")

    print("测试完成 - 代码生成阶段成功")

except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()