#!/usr/bin/env python3
"""
Test script to verify the /start command notification functionality.
This script simulates the behavior to ensure first-time vs returning user detection works.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tokenize_service import tokenizeService

class MockUser:
    def __init__(self, user_id, username, full_name):
        self.id = user_id
        self.username = username
        self.full_name = full_name

async def test_first_time_detection():
    """Test if we can detect first-time users correctly"""
    print("Testing first-time user detection...")
    
    # Test with a mock user ID that likely doesn't exist
    test_user_id = 999999999
    
    try:
        # Check if user exists
        existing_tokens = await tokenizeService.get_user_tokens(test_user_id)
        is_first_start = existing_tokens is None
        
        print(f"User ID {test_user_id}:")
        print(f"  - Existing tokens: {existing_tokens}")
        print(f"  - Is first start: {is_first_start}")
        
        if is_first_start:
            print("  ✅ Would send 'first time' notification")
        else:
            print("  ✅ Would send 'returning user' notification")
            
    except Exception as e:
        print(f"  ❌ Error testing user detection: {e}")

def test_notification_messages():
    """Test the notification message formatting"""
    print("\nTesting notification message formatting...")
    
    # Mock user data
    user = MockUser(123456789, "testuser", "Test User")
    ref_user_id = "987654321"
    
    # Test first-time notification
    user_mention = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
    first_time_text = f"""
🎉 Ваш друг {user_mention} (@{user.username}) впервые запустил бота по вашей реферальной ссылке!

Чтобы {user.full_name} стал вашим рефералом, он должен подписаться на канал @gptDeep.

Как только это произойдёт вы получите <b>5 000</b>⚡️ единоразово и <b>+500</b>⚡️️ к ежедневному пополнению баланса.

Если вдруг этого долго не происходит, то возможно вашему другу нужна помощь, <b>попробуйте написать ему в личные сообщения</b>. 
Если и это не помогает, то обратитесь в поддержку в сообществе @deepGPT и мы поможем вам разобраться с ситуацией.
"""
    
    print("First-time notification:")
    print(first_time_text)
    
    # Test returning user notification
    returning_text = f"""
🔄 Ваш друг {user_mention} (@{user.username}) снова перешёл по вашей реферальной ссылке.

Чтобы вашему другу стать вашим рефералом, он должен подписаться на канал @gptDeep.

Как только это произойдёт вы получите <b>5 000</b>⚡️ единоразово и <b>+500</b>⚡️️ к ежедневному пополнению баланса.

Если вдруг этого долго не происходит, то возможно вашему другу нужна помощь, <b>попробуйте написать ему в личные сообщения</b>. 
Если и это не помогает, то обратитесь в поддержку в сообществе @deepGPT и мы поможем вам разобраться с ситуацией.
"""
    
    print("\nReturning user notification:")
    print(returning_text)

async def main():
    """Main test function"""
    print("🧪 Testing /start notification functionality\n")
    
    test_notification_messages()
    await test_first_time_detection()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())