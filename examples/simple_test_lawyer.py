#!/usr/bin/env python3
"""
Simple test to verify lawyer system message exists and has correct content
"""

import sys
import os

# Add the parent directory to Python path  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lawyer_system_message():
    print("Testing lawyer system message integration...")
    
    # Import the actual system message
    from bot.gpt.db_system_message import lawyer_system_message
    
    # Test 1: Check if lawyer_system_message exists and is not empty
    assert lawyer_system_message, "lawyer_system_message is empty or None"
    print("✅ lawyer_system_message exists and is not empty")
    
    # Test 2: Check system message content contains expected legal terms
    assert "юрист-консультант" in lawyer_system_message.lower(), "System message doesn't contain 'юрист-консультант'"
    assert "правовые нормы" in lawyer_system_message.lower(), "System message doesn't contain 'правовые нормы'"
    assert "законов" in lawyer_system_message.lower(), "System message doesn't contain 'законов'"
    print("✅ Lawyer system message contains appropriate legal consultation content")
    
    # Test 3: Check structure
    assert "###ИНСТРУКЦИИ###" in lawyer_system_message, "System message doesn't have proper instructions header"
    assert "###Правила ответов###" in lawyer_system_message, "System message doesn't have proper answering rules header"
    print("✅ Lawyer system message has proper structure")
    
    # Test 4: Check it has the expected format and guidance
    assert "Структурируй ответ:" in lawyer_system_message, "System message doesn't contain answer structure guidance"
    assert "Краткий анализ ситуации" in lawyer_system_message, "System message doesn't contain situation analysis step"
    assert "Применимые правовые нормы" in lawyer_system_message, "System message doesn't contain legal norms step"
    print("✅ Lawyer system message contains proper legal consultation structure")
    
    print("\n🎉 All tests passed! Lawyer system message is properly defined.")
    print(f"System message length: {len(lawyer_system_message)} characters")

if __name__ == "__main__":
    test_lawyer_system_message()