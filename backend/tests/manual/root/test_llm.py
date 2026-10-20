"""
Test script to check LLM service
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

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables directly

def test_llm_service():
    """Test LLM service"""
    print("=" * 60)
    print("Testing LLM service")
    print("=" * 60)

    try:
        from app.services.glm_service import chat

        prompt = "Say 'Hello World' in Chinese"
        print(f"Sending prompt: {prompt}")

        response = chat([{"role": "user", "content": prompt}], max_tokens=100)
        print(f"LLM Response: {response}")

        if response:
            print("✓ LLM service working")
        else:
            print("✗ LLM service returned empty response")

    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_service()