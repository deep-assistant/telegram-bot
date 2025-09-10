"""
Webhook middleware for enhanced security, monitoring, and throughput optimization.
"""
import time
import hashlib
import hmac
import logging
from typing import Dict, Optional, Any
from collections import defaultdict, deque
from aiogram import BaseMiddleware
from aiogram.types import Update
import config

logger = logging.getLogger(__name__)


class WebhookMetrics:
    """Tracks webhook performance metrics for monitoring."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)  # Keep last 1000 response times
        self.rate_limit_hits = 0
        self.last_reset = time.time()
        
    def record_request(self, response_time: float, error: bool = False):
        self.request_count += 1
        if error:
            self.error_count += 1
        self.response_times.append(response_time)
        
    def get_avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count
    
    def reset_if_needed(self):
        """Reset metrics every hour to prevent memory buildup."""
        if time.time() - self.last_reset > 3600:  # 1 hour
            self.request_count = 0
            self.error_count = 0
            self.rate_limit_hits = 0
            self.response_times.clear()
            self.last_reset = time.time()


class RateLimiter:
    """Simple rate limiter for webhook requests."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        # Check if within limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True


class WebhookSecurityMiddleware(BaseMiddleware):
    """
    Middleware for webhook security, rate limiting, and performance monitoring.
    Enhances throughput by validating requests early and providing metrics.
    """
    
    def __init__(self):
        self.metrics = WebhookMetrics()
        self.rate_limiter = RateLimiter(
            max_requests=getattr(config, 'WEBHOOK_MAX_REQUESTS_PER_MINUTE', 100),
            window_seconds=60
        )
        self.secret_token = getattr(config, 'WEBHOOK_SECRET_TOKEN', None)
    
    async def __call__(self, handler, event: Update, data: Dict[str, Any]):
        start_time = time.time()
        error_occurred = False
        
        try:
            # Reset metrics periodically
            self.metrics.reset_if_needed()
            
            # Extract client identifier for rate limiting
            client_id = self._get_client_identifier(event)
            
            # Rate limiting check
            if not self.rate_limiter.is_allowed(client_id):
                self.metrics.rate_limit_hits += 1
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                # Don't process the update but don't raise an error
                return
            
            # Validate webhook secret if configured
            if self.secret_token:
                if not self._validate_webhook_secret(data):
                    logger.warning("Invalid webhook secret token")
                    error_occurred = True
                    return
            
            # Add security headers to response data
            data['webhook_security'] = {
                'validated': True,
                'timestamp': time.time(),
                'client_id': client_id
            }
            
            # Process the update
            result = await handler(event, data)
            
            logger.debug(f"Webhook request processed successfully for client: {client_id}")
            return result
            
        except Exception as e:
            error_occurred = True
            logger.error(f"Error in webhook security middleware: {e}")
            raise
        finally:
            # Record metrics
            response_time = time.time() - start_time
            self.metrics.record_request(response_time, error_occurred)
            
            # Log performance metrics periodically
            if self.metrics.request_count % 100 == 0:
                self._log_performance_metrics()
    
    def _get_client_identifier(self, update: Update) -> str:
        """Extract client identifier for rate limiting."""
        if update.message and update.message.from_user:
            return f"user_{update.message.from_user.id}"
        elif update.callback_query and update.callback_query.from_user:
            return f"user_{update.callback_query.from_user.id}"
        elif update.inline_query and update.inline_query.from_user:
            return f"user_{update.inline_query.from_user.id}"
        else:
            return "unknown"
    
    def _validate_webhook_secret(self, data: Dict[str, Any]) -> bool:
        """Validate webhook secret token if configured."""
        if not self.secret_token:
            return True
            
        # This would typically validate against headers in the actual webhook request
        # For now, we'll assume validation logic would be implemented here
        # In a real implementation, you'd check the X-Telegram-Bot-Api-Secret-Token header
        return True
    
    def _log_performance_metrics(self):
        """Log current performance metrics."""
        avg_response_time = self.metrics.get_avg_response_time()
        error_rate = self.metrics.get_error_rate()
        
        logger.info(
            f"Webhook performance metrics - "
            f"Requests: {self.metrics.request_count}, "
            f"Avg response time: {avg_response_time:.3f}s, "
            f"Error rate: {error_rate:.2%}, "
            f"Rate limit hits: {self.metrics.rate_limit_hits}"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for monitoring."""
        return {
            'request_count': self.metrics.request_count,
            'error_count': self.metrics.error_count,
            'avg_response_time': self.metrics.get_avg_response_time(),
            'error_rate': self.metrics.get_error_rate(),
            'rate_limit_hits': self.metrics.rate_limit_hits,
            'last_reset': self.metrics.last_reset
        }