#!/usr/bin/env python3
"""
Standalone test script for filename extraction functionality.
Contains both the function implementation and tests to avoid import issues.
"""

import re
from urllib.parse import urlparse, unquote
import os


def extract_human_readable_filename(url: str) -> str:
    """
    Extract a human-readable filename from a URL, especially for Discord CDN URLs.
    
    Takes a URL like:
    https://cdn.discordapp.com/attachments/1334433356263194676/1335313374656860181/deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f.png?ex=679fb6fd&is=679e657d&hm=c58ae42143406364740aea7627649988d709ec47c86eacf9340a366a874bdd76&
    
    And returns: deborah_anime_girl.png
    
    Args:
        url (str): The URL to extract filename from
        
    Returns:
        str: Human-readable filename
    """
    try:
        # Parse URL and get the path
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        
        # Get filename from path
        filename = os.path.basename(path)
        
        if not filename:
            return "image.png"
            
        # Split filename and extension
        name_part, ext = os.path.splitext(filename)
        
        # If no extension, default to .png
        if not ext:
            ext = ".png"
            
        # For Discord CDN URLs, apply human-readable extraction
        if 'cdn.discordapp.com' in url or 'discord' in url.lower():
            return extract_discord_filename(name_part, ext)
            
        # For other URLs, try to clean up the filename
        return clean_filename(name_part, ext)
        
    except Exception:
        # Fallback to generic name if anything goes wrong
        return "image.png"


def extract_discord_filename(name_part: str, ext: str) -> str:
    """
    Extract human-readable name from Discord CDN filename.
    
    Example: deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f
    Returns: deborah_anime_girl
    """
    # Remove UUID-like patterns (hexadecimal with dashes)
    # Pattern for UUID: 8-4-4-4-12 hex digits
    name_part = re.sub(r'_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '', name_part)
    
    # Remove other hex patterns and numbers at the end
    name_part = re.sub(r'_[0-9a-fA-F]{6,}$', '', name_part)
    name_part = re.sub(r'_\d{10,}', '', name_part)  # Remove long numbers like timestamps
    
    # Split by underscores and keep meaningful words
    parts = name_part.split('_')
    meaningful_parts = []
    
    for part in parts:
        # Skip parts that are purely numeric or very short
        if len(part) < 2 or part.isdigit():
            continue
        # Skip parts that look like user IDs or codes (starts with letters followed by mostly numbers)
        # But keep common words that might have some numbers mixed in
        if re.match(r'^[a-zA-Z]+\d{3,}', part):  # Skip things like "user123", "id456" etc
            continue
        meaningful_parts.append(part)
    
    # Take first few meaningful parts
    result_parts = meaningful_parts[:3]  # Limit to avoid very long names
    
    if not result_parts:
        return f"image{ext}"
        
    result_name = '_'.join(result_parts)
    return f"{result_name}{ext}"


def clean_filename(name_part: str, ext: str) -> str:
    """
    Clean up a generic filename to make it more human-readable.
    """
    # Remove query parameters and fragments that might be in the name
    name_part = re.sub(r'[?#].*$', '', name_part)
    
    # Check for a meaningful prefix before a long hex sequence
    prefix_before_hex = re.match(r'^([a-zA-Z]{2,})[0-9a-fA-F]{16,}$', name_part)
    if prefix_before_hex:
        name_part = prefix_before_hex.group(1)
    else:
        # Remove very long hex sequences (16+ characters) from the end
        name_part = re.sub(r'[0-9a-fA-F]{16,}$', '', name_part)
    
    # If the name is empty or too short after cleaning, use a default
    if len(name_part) < 2:
        name_part = "image"
        
    return f"{name_part}{ext}"


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
            "url": "https://api.service.com/generate/image123456789abcdef123456789.png",
            "expected": "image.png",  # Should clean long hex sequences (16+ chars)
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
    exit(main())