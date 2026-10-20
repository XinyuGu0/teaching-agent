"""
Test script to reproduce PPT generation issue where second page doesn't generate
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
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Flask app context
from app import create_app
app = create_app('development')

with app.app_context():
    from app.services.build_sh_generator import get_build_sh_generator

    def test_ppt_generation():
        """Test PPT generation with multiple pages"""
        print("=" * 60)
        print("Testing PPT generation with multiple pages")
        print("=" * 60)

        generator = get_build_sh_generator()

        # Test outline with multiple slides
        outline = {
            'title': '测试多页PPT生成',
            'slides': [
                {
                    'title': '第一页标题',
                    'content': '这是第一页的内容',
                    'type': 'content'
                },
                {
                    'title': '第二页标题',
                    'content': '这是第二页的内容',
                    'type': 'content'
                },
                {
                    'title': '第三页标题',
                    'content': '这是第三页的内容',
                    'type': 'content'
                }
            ]
        }

        output_path = os.path.join(os.path.dirname(__file__), 'test_output.pptx')

        print(f"Output path: {output_path}")
        print(f"Outline: {json.dumps(outline, ensure_ascii=False, indent=2)}")

        try:
            result = generator.generate_with_llm(
                template_id='builtin_science--time-travel',  # 使用一个内置模板
                outline=outline,
                output_path=output_path,
                progress_callback=lambda progress: print(f"Progress: {progress}")
            )

            print("\n" + "=" * 60)
            print("Generation result:")
            print(f"Success: {result.get('success')}")
            if not result.get('success'):
                print(f"Error: {result.get('error')}")

            if result.get('python_code'):
                print("\nGenerated Python code preview:")
                code = result['python_code']
                print(code[:1000] + "..." if len(code) > 1000 else code)

            # Check if file exists
            if os.path.exists(output_path):
                print(f"\n✓ Output file exists: {output_path}")
                print(f"File size: {os.path.getsize(output_path)} bytes")
            else:
                print(f"\n✗ Output file does not exist: {output_path}")

        except Exception as e:
            print(f"\n✗ Exception occurred: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        test_ppt_generation()