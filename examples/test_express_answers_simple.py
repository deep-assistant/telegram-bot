#!/usr/bin/env python3
"""
Simple test script for Express Answers mode implementation.
This script verifies that the new Express Answers mode is properly configured without database dependencies.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_enum_definition():
    """Test that ExpressAnswers is properly defined in SystemMessages enum."""
    print("🧪 Testing SystemMessages enum definition...")
    
    # Import without triggering database connections
    import importlib.util
    
    # Load the module manually
    spec = importlib.util.spec_from_file_location("gpt_service", "services/gpt_service.py")
    gpt_service = importlib.util.module_from_spec(spec)
    
    # Execute the module
    spec.loader.exec_module(gpt_service)
    
    # Check that ExpressAnswers exists
    assert hasattr(gpt_service.SystemMessages, 'ExpressAnswers'), "SystemMessages.ExpressAnswers should exist"
    assert gpt_service.SystemMessages.ExpressAnswers.value == "express_answers", "ExpressAnswers value should be 'express_answers'"
    
    print("✅ SystemMessages enum test passed")
    return gpt_service.SystemMessages


def test_system_message_content():
    """Test that the express answers system message is properly defined."""
    print("🧪 Testing system message content...")
    
    # Read the db_system_message.py file
    with open("bot/gpt/db_system_message.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that express_answers_system_message is defined
    assert "express_answers_system_message" in content, "express_answers_system_message should be defined"
    
    # Check that it contains key instructions
    assert "краткие" in content.lower() or "brief" in content.lower(), "Should mention brief answers"
    assert "да" in content.lower() and "нет" in content.lower(), "Should mention yes/no answers"
    
    print("✅ System message content test passed")


def test_system_messages_mapping():
    """Test that the mapping includes ExpressAnswers."""
    print("🧪 Testing system messages mapping...")
    
    # Read the system_messages.py file
    with open("bot/gpt/system_messages.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check imports
    assert "express_answers_system_message" in content, "Should import express_answers_system_message"
    
    # Check mapping
    assert "SystemMessages.ExpressAnswers.value: express_answers_system_message" in content, "Should map ExpressAnswers"
    
    # Check text representation
    assert "Экспресс-ответы" in content, "Should have Russian text representation"
    assert "⚡" in content, "Should have lightning emoji"
    
    print("✅ System messages mapping test passed")


def test_keyboard_includes_express_answers():
    """Test that the keyboard creation includes ExpressAnswers button."""
    print("🧪 Testing keyboard includes ExpressAnswers...")
    
    # Read the system_messages.py file
    with open("bot/gpt/system_messages.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that ExpressAnswers is included in keyboard creation
    assert "SystemMessages.ExpressAnswers.value" in content, "ExpressAnswers should be in keyboard"
    
    # Count InlineKeyboardButton occurrences to ensure it's added
    button_count = content.count("InlineKeyboardButton(")
    assert button_count >= 7, f"Should have at least 7 buttons (including ExpressAnswers), found {button_count}"
    
    print("✅ Keyboard test passed")


def main():
    """Run all tests."""
    print("🚀 Starting Express Answers mode tests (simple version)...\n")
    
    try:
        system_messages_enum = test_enum_definition()
        test_system_message_content()
        test_system_messages_mapping()
        test_keyboard_includes_express_answers()
        
        print(f"\n🎉 All tests passed! Express Answers mode is properly implemented.")
        print(f"📋 ExpressAnswers enum value: {system_messages_enum.ExpressAnswers.value}")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()