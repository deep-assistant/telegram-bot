import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus

from services.utils import async_get


@dataclass
class SearchResult:
    """Single search result"""
    title: str
    url: str
    snippet: str
    source: str  # Which search engine provided this result
    score: float = 0.0  # Relevance score for reranking


@dataclass
class SearchResponse:
    """Combined search response"""
    results: List[SearchResult]
    query: str
    total_results: int
    sources_used: List[str]


class WebSearchService:
    """Web search service that combines multiple search engines"""
    
    def __init__(self, max_results_per_engine: int = 5):
        self.max_results_per_engine = max_results_per_engine
        self.logger = logging.getLogger(__name__)
    
    async def search(self, query: str, max_results: int = 10) -> SearchResponse:
        """
        Search across multiple engines and combine results
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            SearchResponse with combined and reranked results
        """
        if not query.strip():
            return SearchResponse([], query, 0, [])
        
        # Run searches in parallel
        search_tasks = [
            self._search_duckduckgo(query),
            self._search_bing(query),
            self._search_serper(query),
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results from all engines
        all_results = []
        sources_used = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Search engine {i} failed: {result}")
                continue
            
            if result:
                all_results.extend(result.results)
                sources_used.extend(result.sources_used)
        
        # Remove duplicates and rerank
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rerank_results(unique_results, query)
        
        # Limit to max_results
        final_results = ranked_results[:max_results]
        
        return SearchResponse(
            results=final_results,
            query=query,
            total_results=len(final_results),
            sources_used=list(set(sources_used))
        )
    
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
            
            response = await async_get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            results = []
            
            # Parse related topics and results
            for topic in data.get("RelatedTopics", [])[:self.max_results_per_engine]:
                if "Text" in topic and "FirstURL" in topic:
                    results.append(SearchResult(
                        title=topic.get("Text", "").split(" - ")[0],
                        url=topic.get("FirstURL", ""),
                        snippet=topic.get("Text", ""),
                        source="DuckDuckGo"
                    ))
            
            return SearchResponse(results, query, len(results), ["DuckDuckGo"])
            
        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
            return None
    
    async def _search_bing(self, query: str) -> Optional[SearchResponse]:
        """Search using Bing Web Search API (requires API key)"""
        try:
            # This would require BING_API_KEY in config
            import config
            if not hasattr(config, 'BING_API_KEY') or not config.BING_API_KEY:
                return None
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                "Ocp-Apim-Subscription-Key": config.BING_API_KEY
            }
            params = {
                "q": query,
                "count": self.max_results_per_engine,
                "textDecorations": False,
                "textFormat": "Raw"
            }
            
            response = await async_get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            results = []
            
            for item in data.get("webPages", {}).get("value", []):
                results.append(SearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    source="Bing"
                ))
            
            return SearchResponse(results, query, len(results), ["Bing"])
            
        except Exception as e:
            self.logger.error(f"Bing search failed: {e}")
            return None
    
    async def _search_serper(self, query: str) -> Optional[SearchResponse]:
        """Search using Serper Google Search API"""
        try:
            # This would require SERPER_API_KEY in config
            import config
            if not hasattr(config, 'SERPER_API_KEY') or not config.SERPER_API_KEY:
                return None
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": config.SERPER_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "q": query,
                "num": self.max_results_per_engine
            }
            
            response = await async_get(url, params=data, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            results = []
            
            for item in data.get("organic", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="Google"
                ))
            
            return SearchResponse(results, query, len(results), ["Google"])
            
        except Exception as e:
            self.logger.error(f"Serper search failed: {e}")
            return None
    
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
        """
        Rerank results based on relevance score
        
        Simple scoring based on:
        - Query terms in title (higher weight)
        - Query terms in snippet
        - Source reliability
        """
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


# Global service instance
web_search_service = WebSearchService()