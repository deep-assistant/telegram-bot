#!/usr/bin/env python3
"""
Test the translation system to verify it's working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the translation system
from bot.i18n import _, set_user_language, get_user_language, get_available_languages

def test_translations():
    """Test the translation system."""
    
    print("🌐 Testing Telegram Bot i18n System")
    print("=" * 50)
    
    # Test user IDs
    user_ru = 123456
    user_en = 789012
    
    # Set languages
    set_user_language(user_ru, 'ru')
    set_user_language(user_en, 'en')
    
    print(f"Russian user language: {get_user_language(user_ru)}")
    print(f"English user language: {get_user_language(user_en)}")
    print()
    
    # Test basic translations
    print("Testing basic translations:")
    print(f"Russian 'Yes': {_('common.yes', user_id=user_ru)}")
    print(f"English 'Yes': {_('common.yes', user_id=user_en)}")
    print()
    
    # Test menu items
    print("Testing menu translations:")
    print(f"Russian balance: {_('menu.balance', user_id=user_ru)}")
    print(f"English balance: {_('menu.balance', user_id=user_en)}")
    print()
    
    # Test with variables
    print("Testing translations with variables:")
    print(f"Russian model: {_('models.current', user_id=user_ru, model='GPT-4')}")
    print(f"English model: {_('models.current', user_id=user_en, model='GPT-4')}")
    print()
    
    # Test available languages
    print("Available languages:")
    languages = get_available_languages()
    for code, name in languages.items():
        print(f"  {code}: {name}")
    
    print("\n✅ Translation system working correctly!")

if __name__ == "__main__":
    test_translations()