#!/usr/bin/env python3
"""
Generate translation files from extracted strings for internationalization.
"""

import json
import os
import re
from pathlib import Path

def create_translation_key(text: str, file_path: str = "", line: int = 0) -> str:
    """Create a translation key from text."""
    # Remove file path prefix
    if file_path.startswith('../bot/'):
        file_path = file_path[7:]
    
    # Get module name from file path
    if '/' in file_path:
        module = file_path.split('/')[0]
    else:
        module = 'general'
    
    # Clean text for key generation
    clean_text = re.sub(r'[^\w\s]', '', text)
    words = clean_text.split()[:3]  # Take first 3 words
    key_suffix = '_'.join(w.lower() for w in words if w.isalpha())
    
    if not key_suffix:
        key_suffix = f"text_{line}"
    
    return f"{module}.{key_suffix}"

def load_extracted_strings():
    """Load the extracted strings from JSON."""
    with open('extracted_strings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_translation_dict(strings_data):
    """Generate translation dictionary from extracted strings."""
    translations = {}
    key_counter = {}
    
    for item in strings_data:
        text = item['text'].strip()
        if not text:
            continue
            
        # Create translation key
        base_key = create_translation_key(text, item['file'], item['line'])
        
        # Handle duplicates
        if base_key in key_counter:
            key_counter[base_key] += 1
            key = f"{base_key}_{key_counter[base_key]}"
        else:
            key_counter[base_key] = 0
            key = base_key
        
        # Store original Russian text
        translations[key] = text
    
    return translations

def create_russian_base():
    """Create the Russian translation file (base language)."""
    strings_data = load_extracted_strings()
    translations = generate_translation_dict(strings_data)
    
    # Add additional translations for commands and common phrases
    additional_translations = {
        "commands.start": "/start",
        "commands.help": "/help", 
        "commands.balance": "/balance",
        "commands.model": "/model",
        "commands.system": "/system",
        "commands.clear": "/clear",
        "commands.image": "/image",
        "commands.suno": "/suno",
        "commands.buy": "/buy",
        "commands.referral": "/referral",
        "commands.api": "/api",
        "commands.app": "/app",
        
        # Common responses
        "common.yes": "Да",
        "common.no": "Нет", 
        "common.cancel": "Отмена",
        "common.back": "Назад",
        "common.forward": "Вперед",
        "common.error": "Ошибка",
        "common.success": "Успешно",
        "common.loading": "Загрузка...",
        
        # Units and symbols
        "units.energy": "⚡️",
        "units.rub": "RUB",
        "units.stars": "⭐️",
        
        # Language selection
        "language.select": "Выберите язык",
        "language.changed": "Язык изменен на русский",
        "language.current": "Текущий язык: русский"
    }
    
    translations.update(additional_translations)
    
    return translations

def create_english_translations(russian_translations):
    """Create English translations (manual mapping for now)."""
    # This is a basic mapping - in a real scenario, you'd use professional translation
    translation_map = {
        # Basic responses
        "Да ✅": "Yes ✅",
        "Нет ❌": "No ❌", 
        "Отмена ❌": "Cancel ❌",
        "Назад": "Back",
        "Вперед": "Forward",
        "Проверить ✅": "Check ✅",
        "Подписаться 👊🏻": "Subscribe 👊🏻",
        "Подписаться на канал": "Subscribe to channel",
        "Перегенерировать токен 🔄": "Regenerate token 🔄",
        
        # Menu items  
        "✨ Баланс": "✨ Balance",
        "💎 Пополнить баланс": "💎 Top up balance",
        "🛠️ Сменить модель": "🛠️ Change model",
        "⚙️ Сменить Режим": "⚙️ Change Mode", 
        "🎵 Генерация музыки": "🎵 Music generation",
        "🖼️ Генерация картинки": "🖼️ Image generation",
        "🧹 Очистить контекст": "🧹 Clear context",
        "📖 История диалога": "📖 Chat history",
        "🔗 Реферральная ссылка": "🔗 Referral link",
        "🆘 Помощь": "🆘 Help",
        "💖 Пожертвование": "💖 Donation",
        
        # Generation options
        "Сгенерировать 🔥": "Generate 🔥",
        "Сгенерировать еще? 🔥": "Generate more? 🔥",
        "Cгенерировать Midjourney еще? 🔥": "Generate Midjourney more? 🔥",
        "Cгенерировать Flux еще? 🔥": "Generate Flux more? 🔥",
        "Cгенерировать DALL·E 3 еще? 🔥": "Generate DALL·E 3 more? 🔥",
        "Cгенерировать Suno еще? 🔥": "Generate Suno more? 🔥",
        
        # Models and options
        "🤖 GPT-4o": "🤖 GPT-4o",
        "🦾 GPT-3.5": "🦾 GPT-3.5", 
        "Модель: {model}": "Model: {model}",
        "Размер: {size}": "Size: {size}",
        "Шаги: {steps}": "Steps: {steps}",
        "CFG Scale: {cfg}": "CFG Scale: {cfg}",
        
        # Payment
        "Выбирете способ оплаты": "Choose payment method",
        "Telegram Stars ⭐️": "Telegram Stars ⭐️",
        "Оплата картой 💳": "Card payment 💳",
        "Оплатить {stars} ⭐️": "Pay {stars} ⭐️",
        "⬅️ Назад к выбору способа оплаты": "⬅️ Back to payment method selection",
        
        # Status messages
        "Вы не подписались! 😡": "You didn't subscribe! 😡",
        "Вот ваше изображение в оригинальном качестве": "Here's your image in original quality",
        "Вот картинка в оригинальном качестве": "Here's the image in original quality",
        
        # Placeholders
        "💬 Задай свой вопрос": "💬 Ask your question",
        "Опиши": "Describe",
        
        # Language
        "Выберите язык": "Select language", 
        "Язык изменен на русский": "Language changed to Russian",
        "Текущий язык: русский": "Current language: Russian",
        "язык изменен на английский": "Language changed to English",
        "Текущий язык: английский": "Current language: English"
    }
    
    english_translations = {}
    
    for key, russian_text in russian_translations.items():
        if russian_text in translation_map:
            english_translations[key] = translation_map[russian_text]
        else:
            # For now, keep original text with [RU] prefix to identify untranslated items
            english_translations[key] = f"[RU] {russian_text}"
    
    # Add English-specific additions
    english_translations.update({
        "common.yes": "Yes",
        "common.no": "No",
        "common.cancel": "Cancel", 
        "common.back": "Back",
        "common.forward": "Forward",
        "common.error": "Error",
        "common.success": "Success",
        "common.loading": "Loading...",
        "language.changed": "Language changed to English",
        "language.current": "Current language: English"
    })
    
    return english_translations

def main():
    """Generate all translation files."""
    os.makedirs('../bot/i18n/translations', exist_ok=True)
    
    # Generate Russian (base) translations
    print("Generating Russian translations...")
    russian_translations = create_russian_base()
    
    with open('../bot/i18n/translations/ru.json', 'w', encoding='utf-8') as f:
        json.dump(russian_translations, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(russian_translations)} Russian translations")
    
    # Generate English translations
    print("Generating English translations...")
    english_translations = create_english_translations(russian_translations)
    
    with open('../bot/i18n/translations/en.json', 'w', encoding='utf-8') as f:
        json.dump(english_translations, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(english_translations)} English translations")
    
    # Create template files for other languages (starting with English base)
    other_languages = ['zh', 'hi', 'es', 'ar', 'fr', 'bn', 'pt', 'de', 'ja', 'ko', 'it']
    
    for lang in other_languages:
        print(f"Creating template for {lang}...")
        template = {}
        for key, english_text in english_translations.items():
            # Remove [RU] prefix for template
            if english_text.startswith("[RU] "):
                template[key] = english_text[5:]  # Remove [RU] prefix
            else:
                template[key] = english_text
        
        with open(f'../bot/i18n/translations/{lang}.json', 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"\nCreated translation files for {len(other_languages) + 2} languages")
    print("Next steps:")
    print("1. Review and complete English translations")
    print("2. Get professional translations for other languages")
    print("3. Update bot code to use translation keys")

if __name__ == '__main__':
    main()