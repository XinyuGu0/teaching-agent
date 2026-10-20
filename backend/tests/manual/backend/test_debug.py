
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

#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.build_sh_generator import BuildShPPTGenerator

generator = BuildShPPTGenerator()

# 测试代码
test_code = '''
import subprocess
file_name = 'test.pptx'
subprocess.run(["officecli", "batch", file_name, "--input", "slide1.json"])
'''

page_status = {'successful_pages': [], 'failed_pages': [], 'skipped_pages': []}

# 添加页面错误处理
modified_code = generator._add_page_error_handling(test_code, page_status)

print('Full modified code:')
print(repr(modified_code))

# 尝试编译
try:
    compile(modified_code, '<string>', 'exec')
    print('Code compiles successfully')
except SyntaxError as e:
    print(f'Syntax error: {e}')
    print(f'Error at line {e.lineno}, offset {e.offset}')