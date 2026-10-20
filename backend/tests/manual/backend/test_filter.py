
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

# 测试_filter_officecli_commands方法
generator = BuildShPPTGenerator()

# 测试命令列表过滤
test_commands = [
    {"command": "add", "parent": "/slide[1]", "type": "shape", "props": {"name": "test"}},
    {"command": "set", "path": "/slide[1]//shape[@name='test']", "props": {"text": "Hello"}},
    {"command": "set", "invalid_field": "value", "props": {"text": "Invalid"}},
    {"command": "set", "props": {"text": "Missing path"}}  # 缺少path字段
]

print("原始命令列表:")
for cmd in test_commands:
    print(f"  {cmd}")

filtered_commands = generator._filter_officecli_commands(test_commands)

print(f"\n过滤后剩余 {len(filtered_commands)} 个命令:")
for cmd in filtered_commands:
    print(f"  {cmd}")

# 测试代码字符串过滤
test_code = '''hero_commands = [{"command": "add", "parent": "/slide[1]", "type": "shape", "props": {"name": "test"}}, {"command": "set", "invalid_field": "value", "props": {"text": "Invalid"}}]'''

print(f"\n原始代码:\n{test_code}")
filtered_code = generator._filter_officecli_commands(test_code)
print(f"\n过滤后代码:\n{filtered_code}")