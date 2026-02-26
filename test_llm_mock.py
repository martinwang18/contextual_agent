#!/usr/bin/env python3
"""
Test script to check code logic without actual API calls
"""

import os
import sys
import json
from unittest.mock import Mock, patch

# Add backend to path
sys.path.insert(0, 'backend')

def test_code_structure():
    """Test the code structure and logic"""
    print("=" * 60)
    print("Testing Code Structure (Mock Mode)")
    print("=" * 60)

    print("\n1. Testing imports...")
    try:
        from services.recommendations_service import RecommendationsService
        print("   ✓ Successfully imported RecommendationsService")
    except Exception as e:
        print(f"   ✗ Import error: {str(e)}")
        return False

    print("\n2. Testing service initialization with mock client...")
    try:
        # Set mock env vars
        os.environ['PORTKEY_API_KEY'] = 'test-key'
        os.environ['OPENAI_VIRTUAL_KEY'] = 'test-virtual-key'

        with patch('services.recommendations_service.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            service = RecommendationsService()
            print("   ✓ Service initialized")

            if service.client:
                print("   ✓ Client set correctly")
            else:
                print("   ✗ Client is None")
                return False

    except Exception as e:
        print(f"   ✗ Initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("\n3. Testing _call_gpt4 method structure...")
    try:
        # Create a mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "reasoning": "Test reasoning for holiday shopping",
            "items": [
                {"item": "Christmas Tree", "rationale": "Essential decoration", "category": "Decorations"},
                {"item": "Gift Wrap", "rationale": "Wrap presents", "category": "Supplies"}
            ]
        })

        mock_client.chat.completions.create = Mock(return_value=mock_response)

        result = service._call_gpt4("test prompt")

        if result and isinstance(result, dict):
            print(f"   ✓ _call_gpt4 returns correct format: {type(result)}")
            print(f"   ✓ Has 'reasoning': {'reasoning' in result}")
            print(f"   ✓ Has 'items': {'items' in result}")
        else:
            print(f"   ✗ Unexpected result: {result}")

    except Exception as e:
        print(f"   ✗ Error in _call_gpt4: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("\n4. Testing get_recommendations_for_holidays method...")
    try:
        test_holidays = [
            {'title': 'Christmas', 'description': 'Holiday celebration'}
        ]

        result = service.get_recommendations_for_holidays(test_holidays)

        if isinstance(result, dict):
            print(f"   ✓ Returns dict")
            print(f"   ✓ Has 'items' key: {'items' in result}")
            print(f"   ✓ Has 'reasoning' key: {'reasoning' in result}")

            if 'items' in result and isinstance(result['items'], list):
                print(f"   ✓ Items is a list with {len(result['items'])} items")
            else:
                print(f"   ✗ Items format incorrect: {type(result.get('items'))}")
                return False

            if 'reasoning' in result:
                print(f"   ✓ Reasoning: {result['reasoning'][:80]}...")

            return True
        else:
            print(f"   ✗ Unexpected return type: {type(result)}")
            print(f"   Result: {result}")
            return False

    except Exception as e:
        print(f"   ✗ Error in get_recommendations_for_holidays: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    success = test_code_structure()
    print("\n" + "=" * 60)
    if success:
        print("✅ Code structure tests passed!")
        print("\n💡 Next step: Add OPENAI_VIRTUAL_KEY to config/.env file")
    else:
        print("❌ Code structure tests failed")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
