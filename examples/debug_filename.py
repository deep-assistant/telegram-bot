#!/usr/bin/env python3
import re

def debug_filename(name_part):
    print(f"Original: {name_part}")
    
    # Check if it contains a long hex sequence
    hex_match = re.search(r'[0-9a-fA-F]{16,}', name_part)
    if hex_match:
        print(f"Found hex sequence: {hex_match.group()}")
    else:
        print("No long hex sequence found")
    
    # Check if it ends with hex after some letters
    end_with_hex = re.search(r'([a-zA-Z]+)([0-9a-fA-F]{16,})$', name_part)
    if end_with_hex:
        print(f"Found prefix '{end_with_hex.group(1)}' before hex '{end_with_hex.group(2)}'")
    
    # Try the replacement
    after_hex_removal = re.sub(r'[0-9a-fA-F]{16,}$', '', name_part)
    print(f"After hex removal: '{after_hex_removal}' (length: {len(after_hex_removal)})")
    
    # Check for prefix
    prefix_match = re.match(r'^([a-zA-Z]{2,})', name_part)
    if prefix_match:
        print(f"Found prefix: {prefix_match.group(1)}")
    else:
        print("No prefix found")

# Test the problematic case
debug_filename("image123456789abcdef123456789")