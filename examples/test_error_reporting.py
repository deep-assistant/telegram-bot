#!/usr/bin/env python3
"""
Test script for error reporting functionality
"""
import asyncio
import logging
import sys
import os

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.error_reporting.service import ErrorReportingService


async def test_error_service():
    """Test error reporting service functionality"""
    print("🧪 Testing Error Reporting Service")
    print("=" * 50)
    
    service = ErrorReportingService()
    
    # Test 1: Check admin configuration
    print(f"📋 Admin User IDs: {service.admin_user_ids}")
    
    # Test 2: Test error logging
    print("\n📝 Testing error logging...")
    test_context = {
        'timestamp': '2024-01-01T12:00:00+00:00',
        'user_id': 123456789,
        'chat_id': -123456789,
        'text': 'test message'
    }
    
    try:
        raise ValueError("Test error for logging")
    except ValueError as e:
        await service.report_error(e, test_context)
        print("✅ Error logged successfully")
    
    # Test 3: Read recent errors
    print("\n📖 Reading recent errors...")
    errors = await service.get_recent_errors(limit=5)
    print(f"Found {len(errors)} recent errors")
    
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error['exception_type']}: {error['exception_message']}")
    
    # Test 4: Test message formatting
    print("\n📝 Testing message formatting...")
    if errors:
        formatted = service._format_error_message(errors[0])
        print("Sample formatted message:")
        print("-" * 30)
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        print("-" * 30)
    
    print("\n✅ Error reporting service test completed!")


async def test_middleware():
    """Test error reporting middleware functionality"""
    print("\n🧪 Testing Error Reporting Middleware")
    print("=" * 50)
    
    from bot.error_reporting.middleware import ErrorReportingMiddleware
    from unittest.mock import MagicMock
    
    middleware = ErrorReportingMiddleware()
    
    # Create mock event
    mock_event = MagicMock()
    mock_event.chat.id = -123456789
    mock_event.from_user.id = 123456789
    mock_event.from_user.username = "testuser"
    mock_event.text = "test message"
    mock_event.content_type = "text"
    
    # Test context extraction
    context = middleware._extract_context(mock_event)
    print(f"📋 Extracted context: {context}")
    
    print("\n✅ Middleware test completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(test_error_service())
    asyncio.run(test_middleware())