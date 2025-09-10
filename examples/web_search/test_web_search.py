import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from services.web_search_service import WebSearchService, SearchResult, SearchResponse


class TestWebSearchService:
    """Test cases for WebSearchService"""
    
    def setup_method(self):
        """Setup test cases"""
        self.service = WebSearchService(max_results_per_engine=3)
    
    async def test_empty_query(self):
        """Test search with empty query"""
        result = await self.service.search("")
        assert result.results == []
        assert result.query == ""
        assert result.total_results == 0
        assert result.sources_used == []
    
    async def test_deduplicate_results(self):
        """Test result deduplication"""
        results = [
            SearchResult("Title 1", "https://example.com", "Snippet 1", "Source 1"),
            SearchResult("Title 2", "https://example.com/", "Snippet 2", "Source 2"),  # Same URL
            SearchResult("Title 3", "https://another.com", "Snippet 3", "Source 1"),
        ]
        
        unique_results = self.service._deduplicate_results(results)
        assert len(unique_results) == 2
        assert unique_results[0].url == "https://example.com"
        assert unique_results[1].url == "https://another.com"
    
    def test_rerank_results(self):
        """Test result reranking"""
        query = "python programming"
        results = [
            SearchResult("Java Tutorial", "https://java.com", "Learn Java programming", "Google"),
            SearchResult("Python Programming Guide", "https://python.org", "Learn Python programming", "Google"),
            SearchResult("Programming in Python", "https://example.com", "Advanced Python concepts", "Bing"),
        ]
        
        ranked_results = self.service._rerank_results(results, query)
        
        # Should prioritize results with query terms in title
        assert ranked_results[0].title == "Python Programming Guide"
        assert ranked_results[1].title == "Programming in Python"
        assert ranked_results[2].title == "Java Tutorial"


async def run_tests():
    """Run all tests manually"""
    print("Running WebSearchService tests...")
    
    test_instance = TestWebSearchService()
    
    # Test empty query
    test_instance.setup_method()
    await test_instance.test_empty_query()
    print("✓ Empty query test passed")
    
    # Test deduplication
    test_instance.setup_method()
    await test_instance.test_deduplicate_results()
    print("✓ Deduplication test passed")
    
    # Test reranking
    test_instance.setup_method()
    test_instance.test_rerank_results()
    print("✓ Reranking test passed")
    
    print("All tests passed! ✓")


if __name__ == "__main__":
    asyncio.run(run_tests())