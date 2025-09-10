#!/usr/bin/env python3
"""
Test search integration with DuckDuckGo API (real API call)
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create minimal config
class MockConfig:
    BING_API_KEY = ""
    SERPER_API_KEY = ""
    HTTPX_DISABLE_SSL_VERIFY = False

sys.modules['config'] = MockConfig()

from services.web_search_service import web_search_service

async def test_real_search():
    """Test real search with DuckDuckGo"""
    print("Testing real DuckDuckGo search...")
    
    try:
        # Test with a simple query
        result = await web_search_service.search("python programming", max_results=3)
        
        print(f"Query: {result.query}")
        print(f"Total results: {result.total_results}")
        print(f"Sources used: {result.sources_used}")
        
        if result.results:
            print("\nFirst few results:")
            for i, search_result in enumerate(result.results[:2], 1):
                print(f"{i}. {search_result.title}")
                print(f"   URL: {search_result.url}")
                print(f"   Source: {search_result.source}")
                print(f"   Snippet: {search_result.snippet[:100]}...")
                print()
        
        # Verify basic functionality
        assert result.query == "python programming"
        assert isinstance(result.total_results, int)
        assert isinstance(result.sources_used, list)
        
        print("✓ Real search test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_empty_search():
    """Test empty search handling"""
    print("Testing empty search...")
    
    result = await web_search_service.search("")
    
    assert result.results == []
    assert result.query == ""
    assert result.total_results == 0
    assert result.sources_used == []
    
    print("✓ Empty search test passed!")
    return True

async def main():
    """Run all integration tests"""
    print("Running Web Search Integration Tests...")
    print("=" * 50)
    
    tests = [
        test_empty_search(),
        test_real_search(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    success_count = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Test {i+1} failed with exception: {result}")
        elif result:
            success_count += 1
    
    print("=" * 50)
    print(f"Tests completed: {success_count}/{len(tests)} passed")
    
    if success_count == len(tests):
        print("All integration tests passed! ✓")
        return 0
    else:
        print("Some tests failed ✗")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)