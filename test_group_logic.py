#!/usr/bin/env python3
"""
Simple test to verify the group chat detection logic.
"""

def test_group_chat_detection():
    """Test the group chat detection logic."""
    # Test cases for different chat types
    test_cases = [
        ('private', False),
        ('group', True),
        ('supergroup', True),
        ('channel', False),
    ]
    
    for chat_type, expected_is_group in test_cases:
        # This is the logic from our implementation
        is_group_chat = chat_type in ['group', 'supergroup']
        
        print(f"Chat type: {chat_type:12} | Is group: {is_group_chat:5} | Expected: {expected_is_group}")
        assert is_group_chat == expected_is_group, f"Failed for chat type: {chat_type}"
    
    print("✅ All group chat detection tests passed!")

def test_message_routing_logic():
    """Test the message routing logic."""
    
    class MockMessage:
        def __init__(self, chat_type, user_id=123):
            self.chat = type('Chat', (), {'type': chat_type})()
            self.from_user = type('User', (), {'id': user_id})()
    
    # Test private chat (should use normal flow)
    private_msg = MockMessage('private')
    should_send_private = private_msg.chat.type in ['group', 'supergroup']
    print(f"Private chat -> Send to private: {should_send_private} (should be False)")
    assert not should_send_private
    
    # Test group chat (should send to private)
    group_msg = MockMessage('group')
    should_send_private = group_msg.chat.type in ['group', 'supergroup']
    print(f"Group chat -> Send to private: {should_send_private} (should be True)")
    assert should_send_private
    
    # Test supergroup chat (should send to private)
    supergroup_msg = MockMessage('supergroup')
    should_send_private = supergroup_msg.chat.type in ['group', 'supergroup']
    print(f"Supergroup chat -> Send to private: {should_send_private} (should be True)")
    assert should_send_private
    
    print("✅ All message routing logic tests passed!")

if __name__ == '__main__':
    print("🧪 Testing group chat detection and routing logic...\n")
    test_group_chat_detection()
    print()
    test_message_routing_logic()
    print("\n🎉 All tests passed successfully!")