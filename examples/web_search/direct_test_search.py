#!/usr/bin/env python3
"""
Direct test for web search service functionality without dependencies
"""
import asyncio
from dataclasses import dataclass
from typing import List

@dataclass
class SearchResult:
    """Single search result"""
    title: str
    url: str
    snippet: str
    source: str
    score: float = 0.0

class TestWebSearchService:
    """Test version of WebSearchService"""
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL similarity"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            # Normalize URL for comparison
            normalized_url = result.url.lower().rstrip('/')
            
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_results.append(result)
        
        return unique_results
    
    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Rerank results based on relevance score"""
        query_terms = query.lower().split()
        
        source_weights = {
            "Google": 1.0,
            "Bing": 0.9,
            "DuckDuckGo": 0.8
        }
        
        for result in results:
            score = 0.0
            title_lower = result.title.lower()
            snippet_lower = result.snippet.lower()
            
            # Score based on query terms in title (weight: 3)
            for term in query_terms:
                if term in title_lower:
                    score += 3.0
            
            # Score based on query terms in snippet (weight: 1)
            for term in query_terms:
                if term in snippet_lower:
                    score += 1.0
            
            # Apply source weight
            source_weight = source_weights.get(result.source, 0.5)
            score *= source_weight
            
            result.score = score
        
        # Sort by score descending
        return sorted(results, key=lambda x: x.score, reverse=True)

def test_deduplication():
    """Test result deduplication logic"""
    print("Testing deduplication...")
    service = TestWebSearchService()
    
    results = [
        SearchResult("Title 1", "https://example.com", "Snippet 1", "Source 1"),
        SearchResult("Title 2", "https://example.com/", "Snippet 2", "Source 2"),  # Same URL
        SearchResult("Title 3", "https://another.com", "Snippet 3", "Source 1"),
    ]
    
    unique_results = service._deduplicate_results(results)
    
    assert len(unique_results) == 2, f"Expected 2 unique results, got {len(unique_results)}"
    assert unique_results[0].url == "https://example.com", f"Expected first URL to be https://example.com, got {unique_results[0].url}"
    assert unique_results[1].url == "https://another.com", f"Expected second URL to be https://another.com, got {unique_results[1].url}"
    
    print("✓ Deduplication test passed")

def test_reranking():
    """Test result reranking logic"""
    print("Testing reranking...")
    service = TestWebSearchService()
    
    query = "python programming"
    results = [
        SearchResult("Java Tutorial", "https://java.com", "Learn Java programming", "Google"),
        SearchResult("Python Programming Guide", "https://python.org", "Learn Python programming", "Google"),
        SearchResult("Programming in Python", "https://example.com", "Advanced Python concepts", "Bing"),
    ]
    
    ranked_results = service._rerank_results(results, query)
    
    # Should prioritize results with query terms in title
    assert ranked_results[0].title == "Python Programming Guide", f"Expected 'Python Programming Guide' first, got '{ranked_results[0].title}'"
    assert ranked_results[1].title == "Programming in Python", f"Expected 'Programming in Python' second, got '{ranked_results[1].title}'"
    assert ranked_results[2].title == "Java Tutorial", f"Expected 'Java Tutorial' third, got '{ranked_results[2].title}'"
    
    print("✓ Reranking test passed")

def test_scoring():
    """Test scoring algorithm"""
    print("Testing scoring algorithm...")
    service = TestWebSearchService()
    
    query = "machine learning python"
    results = [
        SearchResult("Machine Learning with Python Tutorial", "https://example1.com", "Learn machine learning using python", "Google"),
        SearchResult("Introduction to Python", "https://example2.com", "Basic python programming", "Bing"),
        SearchResult("Data Science Guide", "https://example3.com", "Data science and machine learning", "DuckDuckGo"),
    ]
    
    ranked_results = service._rerank_results(results, query)
    
    # First result should have highest score (has both terms in title)
    assert ranked_results[0].score > ranked_results[1].score, "First result should have higher score than second"
    assert ranked_results[0].title == "Machine Learning with Python Tutorial", f"Highest scoring result should be first, got '{ranked_results[0].title}'"
    
    print("✓ Scoring test passed")

if __name__ == "__main__":
    print("Running Web Search Service Tests...")
    print("=" * 50)
    
    try:
        test_deduplication()
        test_reranking()
        test_scoring()
        
        print("=" * 50)
        print("All tests passed! ✓")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import sys
        sys.exit(1)