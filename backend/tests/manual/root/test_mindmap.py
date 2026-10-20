"""
Test script for mind map generation
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
sys.path.insert(0, 'backend')

from app.services.glm_service import generate_ppt_outline
import json

# Test data
topic = "Python编程基础"
requirements = {
    'audience': '初学者',
    'slide_count': '10-15',
    'style': '简洁',
    'purpose': '教学'
}

print("Testing PPT outline and mind map generation...")
print(f"Topic: {topic}")
print(f"Requirements: {json.dumps(requirements, ensure_ascii=False)}")
print("\n" + "="*50 + "\n")

try:
    result = generate_ppt_outline(
        topic=topic,
        requirements=requirements,
        context_documents=None
    )

    print("Result structure:")
    print(f"Keys: {result.keys()}")
    print("\n" + "="*50 + "\n")

    if 'title' in result:
        print(f"Title: {result['title']}")

    if 'outline' in result:
        print("\nOutline:")
        print(json.dumps(result['outline'], ensure_ascii=False, indent=2))

    if 'mindmap' in result:
        print("\nMind Map (Markdown):")
        print(result['mindmap'])
    else:
        print("\nNo mindmap found in result")

    print("\n" + "="*50)
    print("Test completed successfully!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
