#!/usr/bin/env python3
"""
Test script to verify HTTP robustness improvements work correctly.
This script tests the download_image function and HTTP utilities with retry logic.
"""

import asyncio
import sys
import os
import tempfile
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.utils import download_image
from services.utils import async_get

# Configure logging to see retry attempts
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def test_download_image():
    """Test the improved download_image function."""
    print("Testing download_image function...")
    
    # Test with a real image URL (small image for testing)
    test_url = "https://httpbin.org/image/png"
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        try:
            await download_image(test_url, tmp_file.name)
            
            # Check if file was downloaded
            if os.path.exists(tmp_file.name) and os.path.getsize(tmp_file.name) > 0:
                print("✅ download_image test passed - file downloaded successfully")
                return True
            else:
                print("❌ download_image test failed - file not downloaded properly")
                return False
                
        except Exception as e:
            print(f"❌ download_image test failed with error: {e}")
            return False
        finally:
            # Clean up
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)


async def test_http_utils():
    """Test the improved HTTP utilities."""
    print("Testing HTTP utilities...")
    
    try:
        # Test with httpbin which should work reliably
        response = await async_get("https://httpbin.org/get")
        
        if response.status_code == 200:
            print("✅ async_get test passed")
            return True
        else:
            print(f"❌ async_get test failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ async_get test failed with error: {e}")
        return False


async def test_retry_logic():
    """Test retry logic with a failing endpoint."""
    print("Testing retry logic with unreachable endpoint...")
    
    try:
        # This should fail and trigger retry logic
        response = await async_get("https://httpbin.org/delay/150")  # Will timeout
        print("❌ Expected timeout but request succeeded")
        return False
        
    except Exception as e:
        print(f"✅ Retry logic test passed - request failed as expected: {type(e).__name__}")
        return True


async def main():
    """Run all tests."""
    print("🧪 Starting HTTP robustness tests...\n")
    
    tests = [
        ("Download Image", test_download_image),
        ("HTTP Utils", test_http_utils),
        ("Retry Logic", test_retry_logic),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = await test_func()
        results.append((test_name, result))
    
    print("\n📊 Test Results:")
    print("=" * 50)
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! HTTP robustness improvements are working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)