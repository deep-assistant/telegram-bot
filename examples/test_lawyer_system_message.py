#!/usr/bin/env python3
"""
Simple test to verify lawyer system message integration
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gpt_service import SystemMessages
from bot.gpt.system_messages import system_messages, text_system_messages
from bot.gpt.db_system_message import lawyer_system_message

def test_lawyer_system_message():
    print("Testing lawyer system message integration...")
    
    # Test 1: Check if Lawyer enum exists
    assert hasattr(SystemMessages, 'Lawyer'), "SystemMessages.Lawyer enum not found"
    assert SystemMessages.Lawyer.value == "lawyer", f"Expected 'lawyer', got '{SystemMessages.Lawyer.value}'"
    print("✅ SystemMessages.Lawyer enum exists and has correct value")
    
    # Test 2: Check if lawyer system message is in system_messages dict
    assert SystemMessages.Lawyer.value in system_messages, "Lawyer system message not found in system_messages dict"
    assert system_messages[SystemMessages.Lawyer.value] == lawyer_system_message, "Lawyer system message content mismatch"
    print("✅ Lawyer system message properly mapped in system_messages dict")
    
    # Test 3: Check if lawyer has display text
    assert SystemMessages.Lawyer.value in text_system_messages, "Lawyer not found in text_system_messages dict"
    expected_text = "⚖️ Юрист"
    assert text_system_messages[SystemMessages.Lawyer.value] == expected_text, f"Expected '{expected_text}', got '{text_system_messages[SystemMessages.Lawyer.value]}'"
    print("✅ Lawyer system message has correct display text")
    
    # Test 4: Check system message content
    assert "юрист-консультант" in lawyer_system_message.lower(), "System message doesn't contain expected legal consultant text"
    assert "правовые нормы" in lawyer_system_message.lower(), "System message doesn't contain expected legal terms"
    print("✅ Lawyer system message contains appropriate legal consultation content")
    
    print("\n🎉 All tests passed! Lawyer system message is properly integrated.")

if __name__ == "__main__":
    test_lawyer_system_message()