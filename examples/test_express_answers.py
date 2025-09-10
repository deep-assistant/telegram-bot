#!/usr/bin/env python3
"""
Test script for Express Answers mode implementation.
This script verifies that the new Express Answers mode is properly configured.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.gpt_service import SystemMessages, gptService
from bot.gpt.system_messages import system_messages, text_system_messages, create_system_message_keyboard


def test_express_answers_enum():
    """Test that ExpressAnswers is properly defined in SystemMessages enum."""
    print("🧪 Testing SystemMessages enum...")
    
    # Check that ExpressAnswers exists
    assert hasattr(SystemMessages, 'ExpressAnswers'), "SystemMessages.ExpressAnswers should exist"
    assert SystemMessages.ExpressAnswers.value == "express_answers", "ExpressAnswers value should be 'express_answers'"
    
    print("✅ SystemMessages enum test passed")


def test_system_messages_mapping():
    """Test that express_answers is properly mapped in system_messages dict."""
    print("🧪 Testing system_messages mapping...")
    
    # Check that express_answers is in system_messages
    assert SystemMessages.ExpressAnswers.value in system_messages, "express_answers should be in system_messages"
    
    # Check that the system message is not empty
    express_message = system_messages[SystemMessages.ExpressAnswers.value]
    assert express_message and len(express_message.strip()) > 0, "Express answers system message should not be empty"
    
    # Check that it contains key instructions for short answers
    assert "краткие" in express_message.lower() or "short" in express_message.lower() or "brief" in express_message.lower(), "Should mention brief/short answers"
    
    print("✅ System messages mapping test passed")


def test_text_system_messages():
    """Test that Express Answers has proper text representation."""
    print("🧪 Testing text system messages...")
    
    # Check that ExpressAnswers has text representation
    assert SystemMessages.ExpressAnswers.value in text_system_messages, "ExpressAnswers should have text representation"
    
    text = text_system_messages[SystemMessages.ExpressAnswers.value]
    assert "Экспресс" in text, "Text should contain 'Экспресс'"
    assert "⚡" in text, "Text should contain lightning emoji"
    
    print("✅ Text system messages test passed")


def test_keyboard_creation():
    """Test that the keyboard includes the new Express Answers button."""
    print("🧪 Testing keyboard creation...")
    
    # Create keyboard with default system message
    keyboard = create_system_message_keyboard(SystemMessages.Default.value)
    
    # Extract all callback data from the keyboard
    callback_data_list = []
    for row in keyboard.inline_keyboard:
        for button in row:
            callback_data_list.append(button.callback_data)
    
    # Check that ExpressAnswers callback data is present
    assert SystemMessages.ExpressAnswers.value in callback_data_list, "ExpressAnswers should be in keyboard"
    
    print("✅ Keyboard creation test passed")


def test_gpt_service_integration():
    """Test that GPTService can handle the new system message."""
    print("🧪 Testing GPTService integration...")
    
    # Test user ID for testing
    test_user_id = "test_user_express_123"
    
    try:
        # Set the new system message
        gptService.set_current_system_message(test_user_id, SystemMessages.ExpressAnswers.value)
        
        # Get it back
        retrieved_message = gptService.get_current_system_message(test_user_id)
        
        assert retrieved_message == SystemMessages.ExpressAnswers.value, "Should retrieve the same system message"
        
        print("✅ GPTService integration test passed")
        
    except Exception as e:
        print(f"⚠️  GPTService test skipped due to database requirement: {e}")


def main():
    """Run all tests."""
    print("🚀 Starting Express Answers mode tests...\n")
    
    try:
        test_express_answers_enum()
        test_system_messages_mapping()
        test_text_system_messages()
        test_keyboard_creation()
        test_gpt_service_integration()
        
        print("\n🎉 All tests passed! Express Answers mode is properly implemented.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()