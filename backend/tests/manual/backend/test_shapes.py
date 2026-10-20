"""测试模板中所有有文本的shape"""

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

import subprocess, json, os, glob

styles_dir = os.path.join(os.path.dirname(__file__), 'OfficeCLI-main', 'examples', 'ppt', 'templates', 'styles')
template_dir = os.path.join(styles_dir, 'science--space-exploration')
pptx_files = glob.glob(os.path.join(template_dir, '*.pptx'))
file = pptx_files[0]
print(f"File: {file}", flush=True)

results = []
for slide_num in range(1, 6):
    result = subprocess.run(
        ['officecli', 'query', file, f'/slide[{slide_num}]', '--json'],
        capture_output=True, text=True, timeout=30,
        shell=(os.name == 'nt'), encoding='utf-8', errors='replace'
    )
    data = json.loads(result.stdout)
    shapes = data['data']['Results'] if isinstance(data, dict) and 'data' in data else []
    text_shapes = []
    for i, s in enumerate(shapes, 1):
        fmt = s.get('format', {})
        name = fmt.get('name', '') if isinstance(fmt, dict) else ''
        text = s.get('text', '')
        if name.startswith('!!') and text:
            text_shapes.append(f'[{i}] {name}: "{text[:60]}"')
    results.append(f'Slide {slide_num}: {len(text_shapes)} text shapes')
    for ts in text_shapes:
        results.append(f'  {ts}')

with open(r'C:\Users\Administrator\Desktop\guowaibao1.1\tmp_shapes_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print('Done', flush=True)
