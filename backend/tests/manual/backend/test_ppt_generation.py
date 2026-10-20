
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

# 测试PPT生成
generator = BuildShPPTGenerator()

# 简单的测试大纲
outline = {
    'title': '测试PPT',
    'slides': [
        {'title': '第一页', 'content': '这是第一页内容'},
        {'title': '第二页', 'content': '这是第二页内容'}
    ]
}

output_path = 'test_output.pptx'

def progress_callback(progress_data):
    print(f"进度: {progress_data.get('progress', 0)}% - {progress_data.get('message', '')}")

try:
    result = generator.generate_with_llm(
        template_id='builtin_builtin_brand--aura-coffee',
        outline=outline,
        output_path=output_path,
        progress_callback=progress_callback
    )
    print(f"PPT生成成功: {result}")
except Exception as e:
    print(f"PPT生成失败: {e}")
    import traceback
    traceback.print_exc()