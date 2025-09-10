#!/usr/bin/env python3
"""
Test script for Midjourney prompt cleaning functionality.
Tests that problematic -- parameters are removed from prompts.
"""

import sys
import os

# Add the project root to the path so we can import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_utils import clean_midjourney_prompt

def test_prompt_cleaning():
    """Test cases for prompt cleaning function."""
    
    test_cases = [
        {
            "input": "A beautiful sunset --ar 16:9",
            "expected": "A beautiful sunset",
            "description": "Remove aspect ratio parameter"
        },
        {
            "input": "Portrait of a cat --v 5 --style raw",
            "expected": "Portrait of a cat",
            "description": "Remove version and style parameters"
        },
        {
            "input": "Landscape painting --seed 12345 --quality 2",
            "expected": "Landscape painting",
            "description": "Remove seed and quality parameters"
        },
        {
            "input": "Abstract art --weird 100 --chaos 50 --stylize 750",
            "expected": "Abstract art",
            "description": "Remove multiple artistic parameters"
        },
        {
            "input": "Simple prompt without parameters",
            "expected": "Simple prompt without parameters",
            "description": "Keep prompt unchanged when no parameters"
        },
        {
            "input": "Prompt with dashes - but not parameters --ar 1:1",
            "expected": "Prompt with dashes - but not parameters",
            "description": "Keep regular dashes, remove parameters"
        },
        {
            "input": "  Messy   spacing   --ar   16:9   --v   5  ",
            "expected": "Messy   spacing",
            "description": "Handle extra whitespace properly"
        },
        {
            "input": "",
            "expected": "",
            "description": "Handle empty string"
        },
        {
            "input": "Text -- more text --ar 2:3",
            "expected": "Text -- more text",
            "description": "Keep double dashes in content, remove parameters"
        }
    ]
    
    print("Testing Midjourney prompt cleaning function...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        result = clean_midjourney_prompt(test_case["input"])
        success = result == test_case["expected"]
        
        print(f"Test {i}: {test_case['description']}")
        print(f"  Input:    '{test_case['input']}'")
        print(f"  Expected: '{test_case['expected']}'")
        print(f"  Result:   '{result}'")
        print(f"  Status:   {'✅ PASS' if success else '❌ FAIL'}")
        print()
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = test_prompt_cleaning()
    sys.exit(0 if success else 1)