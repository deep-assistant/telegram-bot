#!/usr/bin/env python3
"""
Integration example showing how to use the i18n system in the Telegram bot.

This example demonstrates:
1. How to import and use the translation system
2. How to register the language selection router
3. How to update existing code to use translations
4. How to test different languages
"""

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

# Import the translation system
from bot.i18n import _, set_user_language, get_user_language, get_available_languages

# Import the language selection router
from bot.language_selection.router import languageRouter

# Import other routers
from bot.start.router import startRouter
# ... other routers

async def main_integration_example():
    """Example of how to integrate i18n into the main bot."""
    
    # 1. Setup bot and dispatcher (example)
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher()
    
    # 2. Include the language selection router
    dp.include_router(languageRouter)
    dp.include_router(startRouter)
    # ... include other routers
    
    # 3. Example of using translations in handlers
    @dp.message()
    async def echo_handler(message: Message):
        user_id = message.from_user.id
        
        # Get translated text based on user's language preference
        echo_text = _("common.success", user_id=user_id)
        await message.answer(echo_text)
    
    print("Bot integration example ready!")
    print("Available commands:")
    print("  /language - Select language")
    print("  /start - Welcome message")
    print("  Any text - Echo with translation")

def translation_usage_examples():
    """Examples of how to use the translation system in your code."""
    
    # Example user IDs for testing
    user_ru = 123456  # Russian user
    user_en = 789012  # English user
    
    # Set different languages for users
    set_user_language(user_ru, 'ru')
    set_user_language(user_en, 'en')
    
    print("=== Translation Usage Examples ===\n")
    
    # Example 1: Basic translation
    print("1. Basic translations:")
    print(f"Russian: {_('common.yes', user_id=user_ru)}")
    print(f"English: {_('common.yes', user_id=user_en)}")
    print()
    
    # Example 2: Translation with variables
    print("2. Translations with variables:")
    model_name = "GPT-4"
    print(f"Russian: {_('models.current', user_id=user_ru, model=model_name)}")
    print(f"English: {_('models.current', user_id=user_en, model=model_name)}")
    print()
    
    # Example 3: Menu items
    print("3. Menu items:")
    print(f"Russian menu: {_('menu.balance', user_id=user_ru)}")
    print(f"English menu: {_('menu.balance', user_id=user_en)}")
    print()
    
    # Example 4: Error messages
    print("4. Error messages:")
    print(f"Russian error: {_('error.not_enough_energy', user_id=user_ru)}")
    print(f"English error: {_('error.not_enough_energy', user_id=user_en)}")
    print()
    
    # Example 5: Available languages
    print("5. Available languages:")
    languages = get_available_languages()
    for code, name in languages.items():
        print(f"  {code}: {name}")

def update_existing_code_example():
    """Example of how to update existing code to use translations."""
    
    print("\n=== Updating Existing Code ===\n")
    
    # BEFORE: Hardcoded Russian text
    print("BEFORE (hardcoded):")
    print("""
async def old_handler(message: Message):
    await message.answer("✨ Баланс")
    """)
    
    # AFTER: Using translations
    print("AFTER (with i18n):")
    print("""
from bot.i18n import _

async def new_handler(message: Message):
    user_id = message.from_user.id
    balance_text = _("menu.balance", user_id=user_id)
    await message.answer(balance_text)
    """)
    
    # Button example
    print("Button update example:")
    print("BEFORE:")
    print("""
InlineKeyboardButton(text="Да ✅", callback_data="accept")
    """)
    
    print("AFTER:")
    print("""
InlineKeyboardButton(
    text=_("common.yes", user_id=user_id), 
    callback_data="accept"
)
    """)

def testing_example():
    """Example of how to test the i18n system."""
    
    print("\n=== Testing Examples ===\n")
    
    # Test user with different languages
    test_user = 999999
    
    languages_to_test = ['ru', 'en', 'es', 'fr']
    
    for lang in languages_to_test:
        set_user_language(test_user, lang)
        current_lang = get_user_language(test_user)
        welcome_text = _("welcome.hello", user_id=test_user)
        
        print(f"Language: {lang}")
        print(f"Set language: {current_lang}")
        print(f"Welcome text: {welcome_text[:50]}...")
        print("-" * 50)

if __name__ == "__main__":
    print("🌐 Telegram Bot Internationalization (i18n) Integration Example")
    print("=" * 70)
    
    # Show usage examples
    translation_usage_examples()
    
    # Show how to update existing code
    update_existing_code_example()
    
    # Show testing examples
    testing_example()
    
    print("\n✅ Integration complete!")
    print("\nNext steps:")
    print("1. Add 'from bot.language_selection.router import languageRouter' to your main bot file")
    print("2. Use 'dp.include_router(languageRouter)' to register the language router")
    print("3. Update existing message handlers to use _() function")
    print("4. Update keyboard creation to pass user_id for translations")
    print("5. Test with different languages using /language command")
    
    print("\n📝 Notes:")
    print("- All translation keys are in bot/i18n/translations/")
    print("- Add new languages by creating new JSON files")
    print("- User language preferences are stored in memory (add database storage in production)")
    print("- Use professional translation services for non-English languages")