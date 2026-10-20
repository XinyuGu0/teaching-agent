"""
Test GLM outline generation with mindmap
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

# Set up Flask app context
from app import create_app
app = create_app('development')

with app.app_context():
    from app.services.glm_service import generate_ppt_outline
    import json

    # Test data
    topic = "Python编程基础"
    requirements = {
        'audience': '初学者',
        'slide_count': '10',
        'style': '简洁',
        'purpose': '教学'
    }

    print("=" * 60)
    print("Testing PPT outline and mind map generation")
    print("=" * 60)
    print(f"\nTopic: {topic}")
    print(f"Requirements: {json.dumps(requirements, ensure_ascii=False, indent=2)}")
    print("\n" + "=" * 60 + "\n")

    try:
        result = generate_ppt_outline(
            topic=topic,
            requirements=requirements,
            context_documents=None
        )

        print("✓ Generation successful!")
        print("\nResult structure:")
        print(f"  Keys: {list(result.keys())}")

        if 'title' in result:
            print(f"\n  Title: {result['title']}")

        if 'outline' in result:
            print(f"\n  Outline structure:")
            outline = result['outline']
            print(f"    Keys: {list(outline.keys())}")
            if 'slides' in outline:
                print(f"    Number of slides: {len(outline['slides'])}")
                if outline['slides']:
                    print(f"    First slide: {outline['slides'][0].get('title', 'N/A')}")

        if 'mindmap' in result:
            print(f"\n  Mindmap:")
            print(f"    Type: {type(result['mindmap'])}")
            print(f"    Length: {len(result['mindmap'])} characters")
            print(f"    Preview (first 200 chars):")
            print(f"    {result['mindmap'][:200]}...")
        else:
            print("\n  ⚠ WARNING: No mindmap in result!")

        print("\n" + "=" * 60)
        print("Full result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
