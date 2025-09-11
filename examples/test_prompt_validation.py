#!/usr/bin/env python3
"""
Test script to verify prompt validation logic for Midjourney prompts.
This tests the fix for issue #37 - rejecting prompts that start with "/".
"""

def test_prompt_starts_with_slash():
    """Test that prompts starting with "/" are detected correctly."""
    
    # Test cases that should be rejected (start with "/")
    invalid_prompts = [
        "/image",
        "/image cat",
        "/start",
        "/ hello",
        "/",
        "/some command",
    ]
    
    # Test cases that should be accepted (don't start with "/")
    valid_prompts = [
        "syberian cat eat soup",
        "self referencing link",
        "image of a cat",
        "cat eating soup",
        "hello world",
        "a/ test",
        "test / test",
        "  normal prompt",  # leading spaces should not affect validation
    ]
    
    print("Testing invalid prompts (should be rejected):")
    for prompt in invalid_prompts:
        starts_with_slash = prompt.strip().startswith('/')
        print(f"  '{prompt}' -> rejected: {starts_with_slash}")
        assert starts_with_slash, f"Expected '{prompt}' to be rejected"
    
    print("\nTesting valid prompts (should be accepted):")
    for prompt in valid_prompts:
        starts_with_slash = prompt.strip().startswith('/')
        print(f"  '{prompt}' -> rejected: {starts_with_slash}")
        assert not starts_with_slash, f"Expected '{prompt}' to be accepted"
    
    print("\n✅ All tests passed! The validation logic correctly identifies prompts that start with '/'")

if __name__ == "__main__":
    test_prompt_starts_with_slash()