"""
Internationalization (i18n) system for the Telegram bot.
Supports multiple languages with fallback to English.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

# Available languages mapping (ISO 639 codes to language names)
LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',  # Russian (current default)
    'zh': '中文',     # Mandarin Chinese
    'hi': 'हिन्दी',    # Hindi
    'es': 'Español',  # Spanish
    'ar': 'العربية',   # Arabic
    'fr': 'Français', # French
    'bn': 'বাংলা',     # Bengali
    'pt': 'Português', # Portuguese
    'de': 'Deutsch',   # German
    'ja': '日本語',    # Japanese
    'ko': '한국어',    # Korean
    'it': 'Italiano'  # Italian
}

DEFAULT_LANGUAGE = 'ru'  # Current bot is in Russian
FALLBACK_LANGUAGE = 'en'

# Cache for loaded translations
_translations_cache: Dict[str, Dict[str, str]] = {}

# Simple in-memory user language storage (in production, use database)
_user_languages: Dict[int, str] = {}

def _load_translations(language: str) -> Dict[str, str]:
    """Load translations for a specific language."""
    if language in _translations_cache:
        return _translations_cache[language]
    
    translations_dir = Path(__file__).parent / 'translations'
    translation_file = translations_dir / f'{language}.json'
    
    if not translation_file.exists():
        if language != FALLBACK_LANGUAGE:
            # Try to load fallback language
            return _load_translations(FALLBACK_LANGUAGE)
        else:
            # Return empty dict if even fallback doesn't exist
            return {}
    
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations_cache[language] = translations
            return translations
    except Exception as e:
        print(f"Error loading translations for {language}: {e}")
        if language != FALLBACK_LANGUAGE:
            return _load_translations(FALLBACK_LANGUAGE)
        return {}

def get_user_language(user_id: int) -> str:
    """Get user's preferred language."""
    return _user_languages.get(user_id, DEFAULT_LANGUAGE)

def set_user_language(user_id: int, language: str) -> bool:
    """Set user's preferred language."""
    if language not in LANGUAGES:
        return False
    
    _user_languages[user_id] = language
    return True

def get_available_languages() -> Dict[str, str]:
    """Get all available languages."""
    return LANGUAGES.copy()

def get_text(key: str, user_id: Optional[int] = None, language: Optional[str] = None, **kwargs) -> str:
    """
    Get translated text for a specific key.
    
    Args:
        key: Translation key
        user_id: User ID to determine language preference
        language: Override language (if not provided, uses user preference)
        **kwargs: Variables for string formatting
    
    Returns:
        Translated text string
    """
    # Determine language
    if language is None:
        if user_id is not None:
            language = get_user_language(user_id)
        else:
            language = DEFAULT_LANGUAGE
    
    # Load translations
    translations = _load_translations(language)
    
    # Get translation
    text = translations.get(key)
    
    # Fallback to English if not found
    if text is None and language != FALLBACK_LANGUAGE:
        fallback_translations = _load_translations(FALLBACK_LANGUAGE)
        text = fallback_translations.get(key)
    
    # Final fallback to key itself
    if text is None:
        text = key
    
    # Format with provided variables
    try:
        if kwargs:
            text = text.format(**kwargs)
    except Exception as e:
        print(f"Error formatting translation '{key}': {e}")
    
    return text

def invalidate_cache():
    """Clear the translations cache (useful for development)."""
    global _translations_cache
    _translations_cache.clear()