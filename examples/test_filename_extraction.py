#!/usr/bin/env python3
"""
Test script for filename extraction functionality.
Tests the extract_human_readable_filename function with various URL types.
"""

import sys
import os

# Add the parent directory to Python path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.utils import extract_human_readable_filename


def test_discord_url():
    """Test with the Discord CDN URL from the GitHub issue."""
    url = "https://cdn.discordapp.com/attachments/1334433356263194676/1335313374656860181/deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f.png?ex=679fb6fd&is=679e657d&hm=c58ae42143406364740aea7627649988d709ec47c86eacf9340a366a874bdd76&"
    
    result = extract_human_readable_filename(url)
    expected = "deborah_anime_girl.png"
    
    print(f"Discord URL Test:")
    print(f"Input URL: {url}")
    print(f"Expected: {expected}")
    print(f"Got: {result}")
    print(f"Pass: {result == expected}")
    print()
    
    return result == expected


def test_generic_urls():
    """Test with various generic URLs."""
    test_cases = [
        {
            "url": "https://example.com/images/sunset_beach_2023.jpg",
            "expected": "sunset_beach_2023.jpg",
            "description": "Simple filename"
        },
        {
            "url": "https://api.service.com/generate/image123456789abcdef.png",
            "expected": "image.png",  # Should clean hex sequences
            "description": "URL with long hex sequence"
        },
        {
            "url": "https://example.com/mountain.jpeg",
            "expected": "mountain.jpeg",
            "description": "Simple filename with .jpeg extension"
        },
        {
            "url": "https://example.com/path/without/extension",
            "expected": "extension.png",  # Default extension
            "description": "URL without file extension"
        },
        {
            "url": "https://example.com/",
            "expected": "image.png",  # Fallback for empty filename
            "description": "URL with no filename"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        result = extract_human_readable_filename(test_case["url"])
        passed = result == test_case["expected"]
        all_passed = all_passed and passed
        
        print(f"Test {i}: {test_case['description']}")
        print(f"Input: {test_case['url']}")
        print(f"Expected: {test_case['expected']}")
        print(f"Got: {result}")
        print(f"Pass: {passed}")
        print()
    
    return all_passed


def test_discord_variations():
    """Test with various Discord URL patterns."""
    test_cases = [
        {
            "url": "https://cdn.discordapp.com/attachments/123/456/anime_girl_art.png",
            "expected": "anime_girl_art.png",
            "description": "Simple Discord filename"
        },
        {
            "url": "https://cdn.discordapp.com/attachments/123/456/user123_portrait_abcd1234-5678-9012-3456-789012345678.jpg",
            "expected": "portrait.jpg",
            "description": "Discord filename with user ID and UUID"
        },
        {
            "url": "https://media.discordapp.net/attachments/123/456/sunset_photo_final.png?width=800&height=600",
            "expected": "sunset_photo_final.png",
            "description": "Discord media URL with query parameters"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        result = extract_human_readable_filename(test_case["url"])
        passed = result == test_case["expected"]
        all_passed = all_passed and passed
        
        print(f"Discord Variation {i}: {test_case['description']}")
        print(f"Input: {test_case['url']}")
        print(f"Expected: {test_case['expected']}")
        print(f"Got: {result}")
        print(f"Pass: {passed}")
        print()
    
    return all_passed


def main():
    """Run all tests."""
    print("Testing filename extraction functionality")
    print("=" * 50)
    print()
    
    # Test the main Discord URL from the issue
    discord_test = test_discord_url()
    
    # Test generic URLs
    print("Generic URL Tests:")
    print("-" * 20)
    generic_test = test_generic_urls()
    
    # Test Discord variations
    print("Discord Variation Tests:")
    print("-" * 25)
    discord_variations_test = test_discord_variations()
    
    # Summary
    print("Test Summary:")
    print("-" * 15)
    print(f"Discord URL Test: {'PASS' if discord_test else 'FAIL'}")
    print(f"Generic URL Tests: {'PASS' if generic_test else 'FAIL'}")
    print(f"Discord Variations: {'PASS' if discord_variations_test else 'FAIL'}")
    
    all_tests_passed = discord_test and generic_test and discord_variations_test
    print(f"Overall Result: {'ALL TESTS PASSED' if all_tests_passed else 'SOME TESTS FAILED'}")
    
    return 0 if all_tests_passed else 1


if __name__ == "__main__":
    sys.exit(main())