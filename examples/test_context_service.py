#!/usr/bin/env python3
"""
Test script for context service functionality
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.context_service import contextService

def test_context_service():
    """Test the basic functionality of the context service"""
    print("🧪 Testing Context Service")
    print("=" * 40)
    
    test_user_id = "test_user_123"
    test_context_name = "test_conversation"
    test_context_data = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing great! How can I help you today?"},
            {"role": "user", "content": "Can you help me with Python programming?"},
            {"role": "assistant", "content": "Absolutely! I'd be happy to help you with Python programming."}
        ],
        "metadata": {
            "model": "gpt-4",
            "created": datetime.now().isoformat()
        }
    }
    
    # Test saving context
    print(f"📥 Testing saving context '{test_context_name}'...")
    result = contextService.save_context(test_user_id, test_context_name, test_context_data)
    print(f"✅ Save result: {result}")
    
    # Test getting saved contexts
    print(f"\n📚 Testing getting saved contexts...")
    saved_contexts = contextService.get_saved_contexts(test_user_id)
    print(f"📝 Found {len(saved_contexts)} saved contexts:")
    for name, context in saved_contexts.items():
        created_date = context.get('created_at', 'Unknown')
        print(f"  - {name} (created: {created_date})")
    
    # Test getting specific context
    print(f"\n🔍 Testing getting specific context '{test_context_name}'...")
    retrieved_context = contextService.get_context(test_user_id, test_context_name)
    if retrieved_context:
        print(f"✅ Retrieved context successfully")
        messages_count = len(retrieved_context['data'].get('messages', []))
        print(f"📨 Context contains {messages_count} messages")
    else:
        print(f"❌ Failed to retrieve context")
    
    # Test updating last used
    print(f"\n⏰ Testing updating last used timestamp...")
    update_result = contextService.update_last_used(test_user_id, test_context_name)
    print(f"✅ Update result: {update_result}")
    
    # Test saving another context
    print(f"\n📥 Testing saving another context...")
    second_context_name = "coding_help"
    second_context_data = {
        "messages": [
            {"role": "user", "content": "I need help with debugging"},
            {"role": "assistant", "content": "I'd be happy to help! What's the issue?"}
        ]
    }
    contextService.save_context(test_user_id, second_context_name, second_context_data)
    
    # Test listing all contexts again
    print(f"\n📚 Testing listing all contexts after adding second one...")
    all_contexts = contextService.get_saved_contexts(test_user_id)
    print(f"📝 Found {len(all_contexts)} saved contexts:")
    for name, context in all_contexts.items():
        created_date = context.get('created_at', 'Unknown')
        last_used = context.get('last_used', 'Unknown')
        print(f"  - {name}")
        print(f"    Created: {created_date}")
        print(f"    Last used: {last_used}")
    
    # Test deleting context
    print(f"\n🗑️ Testing deleting context '{second_context_name}'...")
    delete_result = contextService.delete_context(test_user_id, second_context_name)
    print(f"✅ Delete result: {delete_result}")
    
    # Verify deletion
    print(f"\n📚 Verifying deletion...")
    final_contexts = contextService.get_saved_contexts(test_user_id)
    print(f"📝 Found {len(final_contexts)} saved contexts after deletion")
    
    # Clean up
    print(f"\n🧹 Cleaning up test data...")
    contextService.delete_context(test_user_id, test_context_name)
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    test_context_service()