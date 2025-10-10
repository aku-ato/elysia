#!/usr/bin/env python3
"""
Test script for Arabic text normalization functions.

Tests both PyArabic-based and fallback regex-based normalization.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from elysia.util.arabic import (
    normalize_arabic_text,
    is_arabic_text,
    remove_arabic_diacritics,
    normalize_alef_variants,
    clean_for_display,
    PYARABIC_AVAILABLE
)

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"


def print_test_result(test_name: str, input_text: str, expected: str, actual: str, passed: bool):
    """Print formatted test result."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {test_name}")
    print(f"  Input:    '{input_text}'")
    print(f"  Expected: '{expected}'")
    print(f"  Actual:   '{actual}'")
    if not passed:
        print(f"  {RED}Difference detected!{RESET}")
    print()


def test_arabic_normalization():
    """Test Arabic text normalization with various cases."""
    
    print(f"\n{CYAN}🧪 Testing Arabic Text Normalization{RESET}")
    print(f"PyArabic Available: {GREEN if PYARABIC_AVAILABLE else YELLOW}{PYARABIC_AVAILABLE}{RESET}")
    print("=" * 60 + "\n")
    
    test_cases = [
        {
            "name": "Diacritics removal",
            "input": "مَرْحَباً بِكُمْ",
            "expected": "مرحبا بكم",
            "description": "Remove Tashkeel diacritics"
        },
        {
            "name": "Alef normalization",
            "input": "الذكاء الإصطناعي",
            "expected": "الذكاء الاصطناعي", 
            "description": "Normalize Alef with Hamza to regular Alef"
        },
        {
            "name": "Hamza normalization",
            "input": "سؤال وإجابة",
            "expected": "سءال واجابة",
            "description": "Normalize Hamza variants"
        },
        {
            "name": "Tatweel removal",
            "input": "الســـــــلام عليكم",
            "expected": "السلام عليكم",
            "description": "Remove Arabic elongation (Tatweel)"
        },
        {
            "name": "Complex text",
            "input": "زِيَارَاتٌ سُلْطَانِيَّةٌ مُتَوَاصِلَةٌ لَا تَتَوَقَّفُ",
            "expected": "زيارات سلطانية متواصلة لا تتوقف",
            "description": "Complex text with multiple diacritics"
        },
        {
            "name": "Multiple spaces",
            "input": "النص    مع     مسافات     كثيرة",
            "expected": "النص مع مسافات كثيرة",
            "description": "Normalize multiple whitespace"
        },
        {
            "name": "Mixed Arabic-English",
            "input": "التعلم الآلي ML في الطب",
            "expected": "التعلم الآلي ML في الطب",
            "description": "Mixed script should preserve Latin"
        },
        {
            "name": "Empty string",
            "input": "",
            "expected": "",
            "description": "Handle empty input"
        },
        {
            "name": "Non-Arabic text", 
            "input": "Hello World!",
            "expected": "Hello World!",
            "description": "Non-Arabic text should be unchanged"
        },
        {
            "name": "Numbers and symbols",
            "input": "النص رقم ١٢٣ والرمز @#",
            "expected": "النص رقم ١٢٣ والرمز @#",
            "description": "Preserve Arabic-Indic numerals and symbols"
        }
    ]
    
    passed_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        actual = normalize_arabic_text(test_case["input"])
        passed = actual == test_case["expected"]
        
        print_test_result(
            test_case["name"],
            test_case["input"], 
            test_case["expected"],
            actual,
            passed
        )
        
        if passed:
            passed_count += 1
    
    # Summary
    print("=" * 60)
    success_rate = (passed_count / total_count) * 100
    color = GREEN if success_rate == 100 else YELLOW if success_rate >= 80 else RED
    
    print(f"📊 Test Results: {color}{passed_count}/{total_count} passed ({success_rate:.1f}%){RESET}")
    
    if success_rate == 100:
        print(f"{GREEN}🎉 All tests passed!{RESET}")
    elif success_rate >= 80:
        print(f"{YELLOW}⚠️  Most tests passed, some edge cases may need attention{RESET}")
    else:
        print(f"{RED}❌ Multiple test failures - normalization needs review{RESET}")
    
    return success_rate == 100


def test_utility_functions():
    """Test individual utility functions."""
    
    print(f"\n{CYAN}🔧 Testing Utility Functions{RESET}")
    print("=" * 60 + "\n")
    
    # Test is_arabic_text
    arabic_tests = [
        ("مرحبا", True),
        ("Hello", False),
        ("مرحبا Hello", True),  # Contains Arabic
        ("", False),
        ("123", False)
    ]
    
    print(f"{BLUE}Testing is_arabic_text:{RESET}")
    for text, expected in arabic_tests:
        result = is_arabic_text(text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} is_arabic_text('{text}') = {result} (expected {expected})")
    
    print()
    
    # Test remove_arabic_diacritics
    diacritic_tests = [
        ("مَرْحَبَا", "مرحبا"),
        ("الْحَمْدُ لِلَّهِ", "الحمد لله"),
        ("Hello", "Hello")  # Non-Arabic unchanged
    ]
    
    print(f"{BLUE}Testing remove_arabic_diacritics:{RESET}")
    for input_text, expected in diacritic_tests:
        result = remove_arabic_diacritics(input_text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} remove_arabic_diacritics('{input_text}') = '{result}' (expected '{expected}')")
    
    print()
    
    # Test normalize_alef_variants
    alef_tests = [
        ("إبراهيم", "ابراهيم"),
        ("أحمد", "احمد"),
        ("آدم", "ادم"),
        ("Hello", "Hello")  # Non-Arabic unchanged
    ]
    
    print(f"{BLUE}Testing normalize_alef_variants:{RESET}")
    for input_text, expected in alef_tests:
        result = normalize_alef_variants(input_text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_alef_variants('{input_text}') = '{result}' (expected '{expected}')")


def benchmark_normalization():
    """Simple benchmark of normalization performance."""
    import time
    
    print(f"\n{CYAN}⚡ Performance Benchmark{RESET}")
    print("=" * 60 + "\n")
    
    # Sample text for benchmarking
    sample_texts = [
        "مَرْحَباً بِكُمْ فِي مُؤْتَمَرِ التِّقْنِيَّةِ",
        "زِيَارَاتٌ سُلْطَانِيَّةٌ مُتَوَاصِلَةٌ لَا تَتَوَقَّفُ، وَمَسِيرَةٌ مُسْتَمِرَّةٌ مِنَ العَطَاءِ",
        "آفَاقٌ جَدِيدَةٌ مِنَ التَّعَاوُنِ المُشْتَرَكِ تُفْتَحُ بَيْنَ البُلْدَانِ",
        "اللَّهُمَّ وَفِّقْ قَائِدَ مَسِيرَتِنَا وَحَكِيمَ رُؤْيَتِنَا"
    ] * 25  # 100 texts total
    
    start_time = time.time()
    
    for text in sample_texts:
        normalize_arabic_text(text)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"Processed {len(sample_texts)} texts in {elapsed:.3f} seconds")
    print(f"Average time per text: {(elapsed/len(sample_texts)*1000):.2f} ms")
    print(f"Texts per second: {len(sample_texts)/elapsed:.1f}")


def main():
    """Run all tests."""
    print(f"\n{BLUE}🔤 Arabic Text Processing Test Suite{RESET}")
    print(f"Testing normalization functions with {'PyArabic' if PYARABIC_AVAILABLE else 'regex fallback'}")
    
    # Run tests
    normalization_passed = test_arabic_normalization()
    test_utility_functions()
    benchmark_normalization()
    
    print(f"\n{CYAN}{'=' * 60}{RESET}")
    
    if normalization_passed:
        print(f"{GREEN}🎯 Arabic normalization is working correctly!{RESET}")
        print("✅ Ready for embedding generation with multilingual-e5-large")
    else:
        print(f"{YELLOW}⚠️  Some normalization issues detected{RESET}")
        print("🔧 Consider reviewing normalization logic")
    
    if not PYARABIC_AVAILABLE:
        print(f"\n{YELLOW}💡 Tip: Install PyArabic for enhanced normalization:{RESET}")
        print("   pip install pyarabic")


if __name__ == "__main__":
    main()