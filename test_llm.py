#!/usr/bin/env python3
"""
Test script to verify LLM/OpenAI integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from services.recommendations_service import RecommendationsService

def test_llm_connection():
    """Test the LLM connection and make a sample call"""
    print("=" * 60)
    print("Testing LLM Connection")
    print("=" * 60)

    # Check environment variables
    print("\n1. Checking environment variables...")
    portkey_key = os.getenv('PORTKEY_API_KEY')
    openai_virtual_key = os.getenv('OPENAI_VIRTUAL_KEY') or os.getenv('OPENAI_VIRTUAL_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    print(f"   PORTKEY_API_KEY: {'✓ Set' if portkey_key else '✗ Missing'}")
    print(f"   OPENAI_VIRTUAL_KEY/OPENAI_VIRTUAL_API_KEY: {'✓ Set' if openai_virtual_key else '✗ Missing'}")
    print(f"   OPENAI_API_KEY: {'✓ Set' if openai_api_key else '✗ Missing'}")

    if not portkey_key:
        print("\n⚠️  PORTKEY_API_KEY is required but not set!")
        return False

    if not openai_virtual_key and not openai_api_key:
        print("\n⚠️  Either OPENAI_VIRTUAL_KEY/OPENAI_VIRTUAL_API_KEY or OPENAI_API_KEY is required!")
        return False

    # Initialize service
    print("\n2. Initializing RecommendationsService...")
    try:
        service = RecommendationsService()
        if service.client:
            print("   ✓ Service initialized successfully")
        else:
            print("   ✗ Service client is None (check logs above)")
            return False
    except Exception as e:
        print(f"   ✗ Error initializing service: {str(e)}")
        return False

    # Test holiday recommendations
    print("\n3. Testing holiday recommendations...")
    test_holidays = [
        {
            'title': 'Christmas',
            'description': 'Christian holiday celebrating the birth of Jesus Christ'
        }
    ]

    try:
        result = service.get_recommendations_for_holidays(test_holidays)

        if isinstance(result, dict):
            print(f"   ✓ Got response in correct format (dict)")
            print(f"   ✓ Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
            print(f"   ✓ Number of items: {len(result.get('items', []))}")

            if result.get('items'):
                print("\n   Sample item:")
                item = result['items'][0]
                print(f"     - Item: {item.get('item', 'N/A')}")
                print(f"     - Category: {item.get('category', 'N/A')}")
                print(f"     - Rationale: {item.get('rationale', 'N/A')[:80]}...")

            return True
        else:
            print(f"   ✗ Unexpected response format: {type(result)}")
            print(f"   Response: {result}")
            return False

    except Exception as e:
        print(f"   ✗ Error making LLM call: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    success = test_llm_connection()
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed - check errors above")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
