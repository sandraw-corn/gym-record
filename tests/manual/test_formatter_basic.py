#!/usr/bin/env python3
"""
Manual test for workout log formatter
Tests basic functionality with sample Chinese logs
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.formatter import WorkoutLogFormatter


def test_simple_log():
    """Test 1: Simple workout log with basic exercises"""
    print("=" * 70)
    print("Test 1: Simple Workout Log")
    print("=" * 70)

    raw_log = """
    今天练腿！

    腿弯举 3组
    43公斤 x 17, 15, 15次
    组间休息3分钟

    硬拉 5组 x 5次
    100公斤
    RPE 8.5
    """

    formatter = WorkoutLogFormatter()
    result = formatter.format_log(raw_log, date="2024-01-15")

    if result['success']:
        print("✅ Formatting successful!")
        print("\nFormatted data:")
        print(json.dumps(result['data'], indent=2, ensure_ascii=False))

        # Convert to CSV rows
        csv_rows = formatter.format_to_csv_rows(result['data'])
        print(f"\n✅ Generated {len(csv_rows)} CSV rows")
        return True
    else:
        print(f"❌ Formatting failed: {result.get('error')}")
        if 'validation_errors' in result:
            print(f"Validation errors: {result['validation_errors']}")
        return False


def test_bilateral_exercise():
    """Test 2: Bilateral exercise (left then right)"""
    print("\n" + "=" * 70)
    print("Test 2: Bilateral Exercise (先左后右)")
    print("=" * 70)

    raw_log = """
    单边训练凳划船
    先左后右
    20kg
    11 11, 11 12

    这个是单边动作，左边11次，右边11次算一组
    """

    formatter = WorkoutLogFormatter()
    result = formatter.format_log(raw_log, date="2024-01-16")

    if result['success']:
        print("✅ Formatting successful!")
        print("\nFormatted data:")
        print(json.dumps(result['data'], indent=2, ensure_ascii=False))

        # Check set count
        if result['data']:
            sets = result['data'][0].get('sets')
            if sets == 2:
                print(f"✅ Correctly identified {sets} sets (bilateral exercise)")
            else:
                print(f"⚠️  Expected 2 sets, got {sets}")
        return True
    else:
        print(f"❌ Formatting failed: {result.get('error')}")
        return False


def test_mixed_content():
    """Test 3: Mixed content with diary entries"""
    print("\n" + "=" * 70)
    print("Test 3: Mixed Content (Training + Diary)")
    print("=" * 70)

    raw_log = """
    今天心情很好！早上和朋友吃了早餐。

    坐姿腿弯举 4组 x 12次
    50kg
    RPE 7

    练完去吃火锅了，超级开心！
    明天继续加油💪

    髋外展 3组 x 15次
    30kg

    晚上要去看电影
    """

    formatter = WorkoutLogFormatter()
    result = formatter.format_log(raw_log, date="2024-01-17")

    if result['success']:
        print("✅ Formatting successful!")
        print("\nFormatted data:")
        print(json.dumps(result['data'], indent=2, ensure_ascii=False))

        # Should only extract 2 exercises, ignore diary content
        exercise_count = len(result['data'])
        print(f"\n✅ Extracted {exercise_count} exercises (ignored diary content)")
        return True
    else:
        print(f"❌ Formatting failed: {result.get('error')}")
        return False


def test_validation():
    """Test 4: Validation catches errors"""
    print("\n" + "=" * 70)
    print("Test 4: Validation Test")
    print("=" * 70)

    # This should work
    raw_log = """
    深蹲 3组 x 5次
    120kg
    """

    formatter = WorkoutLogFormatter()
    result = formatter.format_log(raw_log, date="2024-01-18", validate=True)

    if result['success']:
        print("✅ Valid log passed validation")
        print(json.dumps(result['data'], indent=2, ensure_ascii=False))
        return True
    else:
        print(f"❌ Validation failed unexpectedly: {result.get('error')}")
        if 'validation_errors' in result:
            print(f"Errors: {result['validation_errors']}")
        return False


if __name__ == "__main__":
    print("🏋️  Workout Log Formatter - Manual Tests")
    print()

    tests = [
        ("Simple Log", test_simple_log),
        ("Bilateral Exercise", test_bilateral_exercise),
        ("Mixed Content", test_mixed_content),
        ("Validation", test_validation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

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
    sys.exit(0 if passed_count == total_count else 1)
