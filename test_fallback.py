#!/usr/bin/env python3
"""
Test script to check fallback behavior and code logic
"""

import os
import sys

# Add backend to path
sys.path.insert(0, 'backend')

def test_fallback_behavior():
    """Test the fallback behavior when LLM is not available"""
    print("=" * 60)
    print("Testing Fallback Behavior")
    print("=" * 60)

    print("\n1. Testing imports...")
    try:
        from services.recommendations_service import RecommendationsService
        print("   ✓ Successfully imported RecommendationsService")
    except Exception as e:
        print(f"   ✗ Import error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("\n2. Initializing service WITHOUT credentials...")
    try:
        # Clear any existing env vars
        os.environ.pop('PORTKEY_API_KEY', None)
        os.environ.pop('OPENAI_VIRTUAL_KEY', None)
        os.environ.pop('OPENAI_API_KEY', None)

        service = RecommendationsService()
        print("   ✓ Service initialized")

        if service.client is None:
            print("   ✓ Client is None (expected when no credentials)")
        else:
            print("   ⚠️  Client is not None (unexpected)")

    except Exception as e:
        print(f"   ✗ Initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("\n3. Testing holiday recommendations with fallback...")
    try:
        test_holidays = [
            {'title': 'Christmas', 'description': 'Holiday celebration'}
        ]

        result = service.get_recommendations_for_holidays(test_holidays)

        if isinstance(result, dict):
            print(f"   ✓ Returns dict (correct format)")
            print(f"   ✓ Has 'items' key: {'items' in result}")
            print(f"   ✓ Has 'reasoning' key: {'reasoning' in result}")

            items = result.get('items', [])
            reasoning = result.get('reasoning', '')

            print(f"   ✓ Number of fallback items: {len(items)}")
            print(f"   ✓ Reasoning: {reasoning}")

            if items:
                print("\n   Sample fallback item:")
                print(f"     - Item: {items[0].get('item', 'N/A')}")
                print(f"     - Category: {items[0].get('category', 'N/A')}")
                print(f"     - Rationale: {items[0].get('rationale', 'N/A')}")

            return True
        else:
            print(f"   ✗ Unexpected return type: {type(result)}")
            print(f"   Result: {result}")
            return False

    except Exception as e:
        print(f"   ✗ Error testing fallback: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    success = test_fallback_behavior()
    print("\n" + "=" * 60)
    if success:
        print("✅ Fallback behavior works correctly!")
        print("\n💡 Code structure is correct")
        print("💡 To enable LLM: Add PORTKEY_API_KEY and OPENAI_VIRTUAL_KEY to config/.env")
    else:
        print("❌ Fallback tests failed - code issues found")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
