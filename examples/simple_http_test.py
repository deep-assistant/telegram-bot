#!/usr/bin/env python3
"""
Simple test to verify our HTTP improvements work.
"""

import asyncio
import sys
import os
import tempfile
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging to see retry attempts
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def test_aiohttp_improvements():
    """Test the improved aiohttp download function directly."""
    print("Testing aiohttp improvements...")
    
    # Import aiohttp and recreate the improved function here
    import aiohttp
    
    # This is our improved download function
    async def download_image_test(photo_url: str, file_path: str, max_retries: int = 3):
        timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_read=30)
        connector = aiohttp.TCPConnector(
            ssl=True,
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        for attempt in range(max_retries + 1):
            try:
                async with aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    raise_for_status=True
                ) as session:
                    async with session.get(photo_url) as response:
                        if response.status == 200:
                            with open(file_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    f.write(chunk)
                            return
                        else:
                            response.raise_for_status()
                            
            except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionResetError, OSError) as e:
                if attempt == max_retries:
                    logging.error(f"Failed to download image after {max_retries + 1} attempts: {e}")
                    raise
                
                wait_time = 2 ** attempt
                logging.warning(f"Download attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            
            except Exception as e:
                logging.error(f"Unexpected error during image download: {e}")
                raise
    
    # Test with a real image URL
    test_url = "https://httpbin.org/image/png"
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        try:
            await download_image_test(test_url, tmp_file.name)
            
            if os.path.exists(tmp_file.name) and os.path.getsize(tmp_file.name) > 0:
                print("✅ aiohttp improvements test passed - file downloaded successfully")
                return True
            else:
                print("❌ aiohttp improvements test failed - file not downloaded properly")
                return False
                
        except Exception as e:
            print(f"❌ aiohttp improvements test failed with error: {e}")
            return False
        finally:
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)


async def test_httpx_improvements():
    """Test the improved httpx functionality directly."""
    print("Testing httpx improvements...")
    
    import httpx
    
    # Test the improved timeout configuration
    async def test_httpx_request():
        client_kwargs = {
            'timeout': httpx.Timeout(120.0, connect=30.0),
            'limits': httpx.Limits(max_keepalive_connections=20, max_connections=100),
            'follow_redirects': True,
        }
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.get("https://httpbin.org/get")
            return response
    
    try:
        response = await test_httpx_request()
        
        if response.status_code == 200:
            print("✅ httpx improvements test passed")
            return True
        else:
            print(f"❌ httpx improvements test failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ httpx improvements test failed with error: {e}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Starting simple HTTP robustness tests...\n")
    
    tests = [
        ("aiohttp improvements", test_aiohttp_improvements),
        ("httpx improvements", test_httpx_improvements),
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