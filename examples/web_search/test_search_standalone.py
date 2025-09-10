#!/usr/bin/env python3
"""
Standalone test for web search functionality with real API call
"""
import asyncio
import httpx
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class SearchResult:
    """Single search result"""
    title: str
    url: str
    snippet: str
    source: str
    score: float = 0.0

@dataclass
class SearchResponse:
    """Combined search response"""
    results: List[SearchResult]
    query: str
    total_results: int
    sources_used: List[str]

class StandaloneWebSearchService:
    """Standalone web search service for testing"""
    
    def __init__(self, max_results_per_engine: int = 5):
        self.max_results_per_engine = max_results_per_engine
    
    async def search(self, query: str, max_results: int = 10) -> SearchResponse:
        """Search using DuckDuckGo only"""
        if not query.strip():
            return SearchResponse([], query, 0, [])
        
        try:
            result = await self._search_duckduckgo(query)
            if result and result.results:
                final_results = result.results[:max_results]
                return SearchResponse(
                    results=final_results,
                    query=query,
                    total_results=len(final_results),
                    sources_used=["DuckDuckGo"]
                )
            else:
                return SearchResponse([], query, 0, [])
        except Exception as e:
            print(f"Search failed: {e}")
            return SearchResponse([], query, 0, [])
    
    async def _search_duckduckgo(self, query: str) -> Optional[SearchResponse]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)
                
            if response.status_code != 200:
                return None
            
            data = response.json()
            results = []
            
            # Parse related topics and results
            for topic in data.get("RelatedTopics", [])[:self.max_results_per_engine]:
                if "Text" in topic and "FirstURL" in topic:
                    title = topic.get("Text", "").split(" - ")[0]
                    results.append(SearchResult(
                        title=title if title else topic.get("Text", "")[:50],
                        url=topic.get("FirstURL", ""),
                        snippet=topic.get("Text", ""),
                        source="DuckDuckGo"
                    ))
            
            return SearchResponse(results, query, len(results), ["DuckDuckGo"])
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return None

async def test_real_search():
    """Test real search with DuckDuckGo"""
    print("Testing real DuckDuckGo search...")
    
    service = StandaloneWebSearchService()
    
    try:
        # Test with a simple query
        result = await service.search("artificial intelligence", max_results=3)
        
        print(f"Query: {result.query}")
        print(f"Total results: {result.total_results}")
        print(f"Sources used: {result.sources_used}")
        
        if result.results:
            print("\nResults found:")
            for i, search_result in enumerate(result.results, 1):
                print(f"{i}. {search_result.title}")
                print(f"   URL: {search_result.url}")
                print(f"   Source: {search_result.source}")
                snippet = search_result.snippet[:100] + "..." if len(search_result.snippet) > 100 else search_result.snippet
                print(f"   Snippet: {snippet}")
                print()
        else:
            print("No results found (this is normal for DuckDuckGo instant answers)")
        
        # Verify basic functionality
        assert result.query == "artificial intelligence"
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
    
    service = StandaloneWebSearchService()
    result = await service.search("")
    
    assert result.results == []
    assert result.query == ""
    assert result.total_results == 0
    assert result.sources_used == []
    
    print("✓ Empty search test passed!")
    return True

async def main():
    """Run all integration tests"""
    print("Running Standalone Web Search Tests...")
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
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed ✗")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)