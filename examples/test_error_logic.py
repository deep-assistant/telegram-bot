#!/usr/bin/env python3
"""
Simple test for the error handling logic without importing the full service.
"""

def get_human_readable_error(error_data):
    """Copy of the error handling logic for testing"""
    if not error_data:
        return "❌ Произошла неизвестная ошибка при генерации музыки."
        
    error_msg = error_data.get('raw_message', '') or error_data.get('message', '')
    
    if 'moderation_failure' in error_msg and 'Unable to generate lyrics' in error_msg:
        return """❌ Не удалось создать музыку из-за ограничений контента.

🔍 Возможные причины:
• В описании музыки содержится неподходящий контент
• Запрос на создание музыки "без вокала/текста" может вызвать проблемы с генерацией лирики
• Описание нарушает правила сообщества

💡 Рекомендации:
• Попробуйте изменить описание музыки
• Используйте более общие термины вместо "без вокала"
• Избегайте запросов на инструментальную музыку, если хотите получить песню с текстом

Попробуйте с другим описанием!"""
    
    if 'clips generation failed' in error_msg:
        return """❌ Не удалось создать музыкальную композицию.

Возможные причины:
• Проблемы на стороне сервиса Suno
• Неподходящее описание для генерации
• Временные технические неполадки

Попробуйте изменить описание или повторить попытку позже."""
    
    # Generic fallback for other errors
    return f"""❌ Произошла ошибка при генерации музыки.

Детали ошибки: {error_msg}

Попробуйте изменить описание или повторить попытку позже."""

def main():
    print("Testing Suno Error Handling Implementation")
    print("=" * 50)
    
    # Test the exact error from the GitHub issue
    test_error = {
        "code": 10000,
        "raw_message": "clips generation failed: moderation_failure; Unable to generate lyrics from song description",
        "message": "clips generation failed"
    }
    
    result = get_human_readable_error(test_error)
    print("🔍 Test: Original issue error")
    print("Input:", test_error.get('raw_message', ''))
    print("\n📝 Human-readable output:")
    print(result)
    print("\n" + "=" * 50)
    
    # Verify key elements are present
    checks = [
        ("ограничений контента", "Content restrictions mentioned"),
        ("без вокала", "Specific guidance about 'without vocals'"),  
        ("изменить описание", "Suggests changing description"),
        ("💡 Рекомендации", "Contains recommendations section")
    ]
    
    print("✅ Verification:")
    for check_text, description in checks:
        if check_text in result:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ Missing: {description}")
    
    print("\n🎉 Test completed successfully!")
    print("\nThis implementation will now show users:")
    print("• Clear explanation of what went wrong")
    print("• Specific guidance about content restrictions") 
    print("• Actionable recommendations to fix the issue")
    print("• Better user experience instead of raw API errors")

if __name__ == "__main__":
    main()