#!/usr/bin/env python3
"""
Script to extract all user-facing text strings from the Telegram bot codebase
that need to be translated for internationalization.
"""

import os
import re
import ast
import json
from pathlib import Path

def extract_strings_from_file(file_path):
    """Extract text strings from a Python file."""
    strings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return strings
    
    # Find multi-line strings (triple quoted)
    multiline_pattern = r'"""([^"]*(?:"[^"]*"[^"]*)*)"""'
    multiline_matches = re.findall(multiline_pattern, content, re.DOTALL)
    
    for match in multiline_matches:
        clean_text = match.strip()
        if clean_text and any(ord(c) > 127 for c in clean_text):  # Contains non-ASCII (likely Russian)
            strings.append({
                'file': str(file_path),
                'type': 'multiline',
                'text': clean_text,
                'line': content[:content.find(f'"""{match}"""')].count('\n') + 1
            })
    
    # Find single line strings with Russian text
    single_pattern = r'text\s*=\s*["\']([^"\']*[а-яёА-ЯЁ][^"\']*)["\']'
    single_matches = re.finditer(single_pattern, content)
    
    for match in single_matches:
        strings.append({
            'file': str(file_path),
            'type': 'single',
            'text': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })
    
    # Find f-strings with Russian text
    fstring_pattern = r'f["\']([^"\']*[а-яёА-ЯЁ][^"\']*)["\']'
    fstring_matches = re.finditer(fstring_pattern, content)
    
    for match in fstring_matches:
        strings.append({
            'file': str(file_path),
            'type': 'fstring',
            'text': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })
    
    # Find InlineKeyboardButton text
    button_pattern = r'InlineKeyboardButton\([^)]*text\s*=\s*["\']([^"\']*[а-яёА-ЯЁ][^"\']*)["\']'
    button_matches = re.finditer(button_pattern, content)
    
    for match in button_matches:
        strings.append({
            'file': str(file_path),
            'type': 'button',
            'text': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })
    
    # Find KeyboardButton text
    kbd_pattern = r'KeyboardButton\([^)]*text\s*=\s*["\']([^"\']*[а-яёА-ЯЁ][^"\']*)["\']'
    kbd_matches = re.finditer(kbd_pattern, content)
    
    for match in kbd_matches:
        strings.append({
            'file': str(file_path),
            'type': 'keyboard',
            'text': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })
    
    return strings

def main():
    """Main function to extract all strings."""
    bot_dir = Path('../bot')
    all_strings = []
    
    for py_file in bot_dir.rglob('*.py'):
        file_strings = extract_strings_from_file(py_file)
        all_strings.extend(file_strings)
    
    # Sort by file and line number
    all_strings.sort(key=lambda x: (x['file'], x['line']))
    
    # Save to JSON for analysis
    with open('extracted_strings.json', 'w', encoding='utf-8') as f:
        json.dump(all_strings, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"Extracted {len(all_strings)} text strings from {len(set(s['file'] for s in all_strings))} files")
    print("\nBy type:")
    type_counts = {}
    for s in all_strings:
        type_counts[s['type']] = type_counts.get(s['type'], 0) + 1
    
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count}")
    
    print(f"\nResults saved to extracted_strings.json")
    
    # Show some examples
    print("\nFirst 5 examples:")
    for i, string in enumerate(all_strings[:5]):
        print(f"{i+1}. {string['file']}:{string['line']} ({string['type']})")
        print(f"   '{string['text'][:50]}{'...' if len(string['text']) > 50 else ''}'")

if __name__ == '__main__':
    main()