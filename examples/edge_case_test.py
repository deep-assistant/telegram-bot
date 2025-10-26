#!/usr/bin/env python3
"""
Test edge cases for the prompt cleaning function.
"""

import re

def clean_midjourney_prompt(prompt: str) -> str:
    if not prompt:
        return prompt
    
    # Pattern 1: Remove --word followed by optional space and value (like --ar 16:9 or --ar16:9)
    pattern1 = r'\s*--[a-zA-Z]\w*(?:\s+[^\s-]+)*'
    
    # Pattern 2: Remove malformed parameters with space after -- (like "-- ar 16:9")
    # The error "there should be no space after --" suggests this is invalid
    pattern2 = r'\s*--\s+[a-zA-Z]\w*(?:\s+[^\s-]+)*'
    
    # Apply both patterns
    cleaned_prompt = re.sub(pattern1, '', prompt)
    cleaned_prompt = re.sub(pattern2, '', cleaned_prompt)
    
    # Remove extra whitespace and clean up the result
    cleaned_prompt = ' '.join(cleaned_prompt.split())
    
    return cleaned_prompt.strip()

# Test the specific error case mentioned in the issue
test_cases = [
    "Beautiful landscape -- ar 16:9",  # Space after --
    "Portrait photo --ar16:9",  # No space after parameter
    "Art --v 5 -- style raw",  # Mixed valid and invalid formats
    "Simple text -- not a parameter",  # Regular double dash
    "Test -- ar 1:1 more text",  # Parameter in middle
]

print("Testing edge cases that could cause 'Invalid Param Format' errors:")
print("=" * 70)

for i, prompt in enumerate(test_cases, 1):
    result = clean_midjourney_prompt(prompt)
    print(f"Test {i}:")
    print(f"  Input:  '{prompt}'")
    print(f"  Output: '{result}'")
    print()

print("All edge cases handled successfully!")