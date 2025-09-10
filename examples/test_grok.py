#!/usr/bin/env python3
"""
Test script for Grok integration
"""
import sys
import os
import asyncio

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gpt_service import GPTModels
from services.completions_service import CompletionsService

# Mock XAI_API_KEY for testing (you would set this in config.py)
try:
    from config import XAI_API_KEY
    if not XAI_API_KEY:
        print("❌ XAI_API_KEY not set in config.py")
        print("Please add your Grok API key from console.x.ai to config.py")
        sys.exit(1)
except ImportError:
    print("❌ config.py not found")
    print("Please create config.py from config.example.py and add your XAI_API_KEY")
    sys.exit(1)

async def test_grok_integration():
    """Test Grok API integration"""
    print("🧪 Testing Grok integration...")
    
    completions_service = CompletionsService()
    
    # Test data
    user_id = "test_user"
    message = "Hello, this is a test message. Please respond with a brief greeting."
    system_message = "You are a helpful assistant."
    
    # Test Grok-2
    print("\n🤖 Testing Grok-2...")
    try:
        result = await completions_service.query_ai(
            user_id=user_id,
            message=message,
            system_message=system_message,
            gpt_model="grok-2",
            bot_model=GPTModels.Grok_2,
            singleMessage=True
        )
        
        if result['success']:
            print(f"✅ Grok-2 Response: {result['response'][:100]}...")
            print(f"📊 Model: {result['model']}")
        else:
            print(f"❌ Grok-2 Error: {result['response']}")
    except Exception as e:
        print(f"❌ Grok-2 Exception: {str(e)}")
    
    # Test Grok-2 Mini
    print("\n🤖 Testing Grok-2 Mini...")
    try:
        result = await completions_service.query_ai(
            user_id=user_id,
            message=message,
            system_message=system_message,
            gpt_model="grok-2-mini",
            bot_model=GPTModels.Grok_2_mini,
            singleMessage=True
        )
        
        if result['success']:
            print(f"✅ Grok-2 Mini Response: {result['response'][:100]}...")
            print(f"📊 Model: {result['model']}")
        else:
            print(f"❌ Grok-2 Mini Error: {result['response']}")
    except Exception as e:
        print(f"❌ Grok-2 Mini Exception: {str(e)}")
    
    print("\n✨ Grok integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_grok_integration())