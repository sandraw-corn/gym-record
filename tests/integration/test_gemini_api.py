#!/usr/bin/env python3
"""
Integration test for Gemini API connectivity
Tests basic API functionality with simple prompts
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai


def test_api_connection():
    """Test basic API connectivity with a simple prompt"""
    print("🔍 Testing Gemini API connection...")

    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        print("   Please add your API key to .env (see .env.example)")
        return False

    print(f"✅ API key found (length: {len(api_key)})")

    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini: {e}")
        return False

    # Test simple generation
    try:
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        print(f"📡 Testing model: {model_name}")

        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'hi' in a friendly way")

        print(f"✅ Response received: {response.text[:100]}...")
        print(f"✅ API connection test PASSED")
        return True

    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False


def test_json_output_mode():
    """Test JSON output mode for structured data extraction"""
    print("\n🔍 Testing JSON output mode...")

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Skipping (no API key)")
        return False

    try:
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        model = genai.GenerativeModel(model_name)

        # Test JSON mode with structured output
        response = model.generate_content(
            "Return a JSON object with two fields: 'greeting' (string) and 'number' (integer). "
            "Set greeting to 'hello' and number to 42.",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )

        print(f"✅ JSON response: {response.text}")

        # Try to parse as JSON
        import json
        data = json.loads(response.text)

        if 'greeting' in data and 'number' in data:
            print(f"✅ JSON structure valid: greeting={data['greeting']}, number={data['number']}")
            print(f"✅ JSON mode test PASSED")
            return True
        else:
            print(f"⚠️  JSON missing expected fields")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"❌ JSON mode test failed: {e}")
        return False


def test_chinese_input():
    """Test handling Chinese input (for workout log parsing)"""
    print("\n🔍 Testing Chinese language input...")

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  Skipping (no API key)")
        return False

    try:
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        model = genai.GenerativeModel(model_name)

        # Test Chinese to English translation
        response = model.generate_content(
            "Translate to English: 腿弯举 3组 x 12次 x 43公斤",
            generation_config={"temperature": 0.1}
        )

        print(f"✅ Chinese input handled: {response.text[:150]}...")

        # Check if response contains "Leg Curl" or similar
        response_lower = response.text.lower()
        if 'leg' in response_lower or 'curl' in response_lower or 'hamstring' in response_lower:
            print(f"✅ Chinese translation test PASSED")
            return True
        else:
            print(f"⚠️  Translation may not be accurate")
            return False

    except Exception as e:
        print(f"❌ Chinese input test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Gemini API Integration Tests")
    print("=" * 70)

    results = []

    # Test 1: Basic connectivity
    results.append(("API Connection", test_api_connection()))

    # Test 2: JSON mode
    results.append(("JSON Output Mode", test_json_output_mode()))

    # Test 3: Chinese input
    results.append(("Chinese Input", test_chinese_input()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    # Exit with appropriate code
    sys.exit(0 if passed_count == total_count else 1)
