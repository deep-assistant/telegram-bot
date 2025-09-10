"""
Comprehensive tests for webhook functionality and performance optimizations.
"""
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
import pytest
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, User, Chat
from aiogram.fsm.storage.memory import MemoryStorage

from bot.bot_run import create_webhook_app, create_session
from bot.middlewares.webhook_middleware import WebhookSecurityMiddleware, WebhookMetrics, RateLimiter


class TestWebhookMetrics:
    """Test webhook metrics functionality."""
    
    def test_metrics_initialization(self):
        metrics = WebhookMetrics()
        assert metrics.request_count == 0
        assert metrics.error_count == 0
        assert metrics.rate_limit_hits == 0
        assert metrics.get_avg_response_time() == 0.0
        assert metrics.get_error_rate() == 0.0
    
    def test_record_request_success(self):
        metrics = WebhookMetrics()
        metrics.record_request(0.1, error=False)
        
        assert metrics.request_count == 1
        assert metrics.error_count == 0
        assert metrics.get_avg_response_time() == 0.1
        assert metrics.get_error_rate() == 0.0
    
    def test_record_request_error(self):
        metrics = WebhookMetrics()
        metrics.record_request(0.2, error=True)
        
        assert metrics.request_count == 1
        assert metrics.error_count == 1
        assert metrics.get_avg_response_time() == 0.2
        assert metrics.get_error_rate() == 1.0
    
    def test_multiple_requests(self):
        metrics = WebhookMetrics()
        metrics.record_request(0.1, error=False)
        metrics.record_request(0.3, error=True)
        metrics.record_request(0.2, error=False)
        
        assert metrics.request_count == 3
        assert metrics.error_count == 1
        assert metrics.get_avg_response_time() == 0.2
        assert metrics.get_error_rate() == 1/3


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 60
    
    def test_rate_limiting_within_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
    
    def test_rate_limiting_exceeds_limit(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user1") == False  # Exceeds limit
    
    def test_rate_limiting_different_users(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user2") == True
        assert limiter.is_allowed("user1") == True
        assert limiter.is_allowed("user2") == True
        assert limiter.is_allowed("user1") == False  # user1 exceeds limit
        assert limiter.is_allowed("user2") == False  # user2 exceeds limit


class TestWebhookSecurityMiddleware:
    """Test webhook security middleware."""
    
    @pytest.fixture
    def middleware(self):
        return WebhookSecurityMiddleware()
    
    @pytest.fixture
    def mock_update(self):
        user = User(id=123, is_bot=False, first_name="Test")
        chat = Chat(id=456, type="private")
        message = Message(
            message_id=1,
            from_user=user,
            chat=chat,
            date=int(time.time()),
            content_type="text",
            text="test"
        )
        return Update(update_id=1, message=message)
    
    @pytest.mark.asyncio
    async def test_middleware_processes_request(self, middleware, mock_update):
        """Test that middleware processes requests correctly."""
        handler_called = False
        
        async def mock_handler(event, data):
            nonlocal handler_called
            handler_called = True
            return "success"
        
        result = await middleware(mock_handler, mock_update, {})
        
        assert handler_called
        assert result == "success"
        assert middleware.metrics.request_count == 1
        assert middleware.metrics.error_count == 0
    
    @pytest.mark.asyncio
    async def test_middleware_handles_errors(self, middleware, mock_update):
        """Test that middleware handles errors correctly."""
        async def mock_handler(event, data):
            raise Exception("Test error")
        
        with pytest.raises(Exception, match="Test error"):
            await middleware(mock_handler, mock_update, {})
        
        assert middleware.metrics.request_count == 1
        assert middleware.metrics.error_count == 1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, middleware, mock_update):
        """Test that rate limiting works."""
        # Override rate limiter for testing
        middleware.rate_limiter = RateLimiter(max_requests=1, window_seconds=60)
        
        handler_call_count = 0
        
        async def mock_handler(event, data):
            nonlocal handler_call_count
            handler_call_count += 1
            return "success"
        
        # First request should succeed
        result1 = await middleware(mock_handler, mock_update, {})
        assert handler_call_count == 1
        
        # Second request should be rate limited
        result2 = await middleware(mock_handler, mock_update, {})
        assert handler_call_count == 1  # Handler not called again
        assert middleware.metrics.rate_limit_hits == 1


@pytest.mark.asyncio
class TestWebhookApp:
    """Test webhook application functionality."""
    
    async def test_create_webhook_app(self):
        """Test webhook app creation."""
        dp = Dispatcher(storage=MemoryStorage())
        bot = Mock(spec=Bot)
        
        app = await create_webhook_app(dp, bot)
        
        assert isinstance(app, web.Application)
        # Check that routes are registered
        route_paths = [route.resource.canonical for route in app.router.routes()]
        assert '/health' in route_paths
    
    async def test_health_check_endpoint(self):
        """Test health check endpoint."""
        dp = Dispatcher(storage=MemoryStorage())
        bot = Mock(spec=Bot)
        
        app = await create_webhook_app(dp, bot)
        
        async with aiohttp.ClientSession() as session:
            with patch('config.WEBHOOK_URL', 'https://test.com/webhook'):
                async with aiohttp.test_utils.TestServer(app) as server:
                    async with aiohttp.test_utils.TestClient(server) as client:
                        resp = await client.get('/health')
                        assert resp.status == 200
                        data = await resp.json()
                        assert data['status'] == 'healthy'
                        assert 'timestamp' in data
                        assert data['webhook_url'] == 'https://test.com/webhook'


@pytest.mark.asyncio
class TestConnectionPooling:
    """Test connection pooling optimizations."""
    
    async def test_create_session(self):
        """Test that optimized session is created correctly."""
        async with create_session() as session:
            assert isinstance(session, aiohttp.ClientSession)
            
            # Check connector settings
            connector = session.connector
            assert connector.limit == 100
            assert connector.limit_per_host == 30
            assert connector.keepalive_timeout == 30
            assert connector.enable_cleanup_closed == True
            assert connector.use_dns_cache == True
    
    async def test_session_timeout_configuration(self):
        """Test that session timeout is configured correctly."""
        async with create_session() as session:
            timeout = session.timeout
            assert timeout.total == 30
            assert timeout.connect == 5


class TestWebhookPerformance:
    """Test webhook performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test that webhook can handle concurrent requests."""
        middleware = WebhookSecurityMiddleware()
        
        # Override rate limiter to allow more requests
        middleware.rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
        
        async def mock_handler(event, data):
            await asyncio.sleep(0.01)  # Simulate processing time
            return "success"
        
        # Create multiple mock updates
        user = User(id=123, is_bot=False, first_name="Test")
        chat = Chat(id=456, type="private")
        updates = []
        for i in range(10):
            message = Message(
                message_id=i,
                from_user=user,
                chat=chat,
                date=int(time.time()),
                content_type="text",
                text=f"test{i}"
            )
            updates.append(Update(update_id=i, message=message))
        
        # Process requests concurrently
        start_time = time.time()
        tasks = [
            middleware(mock_handler, update, {})
            for update in updates
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # All requests should succeed
        assert all(result == "success" for result in results)
        assert middleware.metrics.request_count == 10
        assert middleware.metrics.error_count == 0
        
        # Should complete in reasonable time (concurrent processing)
        total_time = end_time - start_time
        assert total_time < 0.2  # Should be much less than 10 * 0.01 = 0.1s
    
    def test_metrics_memory_management(self):
        """Test that metrics don't consume excessive memory."""
        metrics = WebhookMetrics()
        
        # Record many requests (more than the response_times deque limit)
        for i in range(2000):
            metrics.record_request(0.1)
        
        # Deque should be limited to 1000 entries
        assert len(metrics.response_times) == 1000
        assert metrics.request_count == 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])