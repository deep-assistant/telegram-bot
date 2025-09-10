# Webhook Performance Optimizations

This document describes the webhook performance optimizations implemented to increase throughput as requested in issue #61.

## Overview

The webhook implementation has been enhanced with several performance and security optimizations:

1. **Connection Pooling and Keep-Alive**: Optimized HTTP connections for better resource utilization
2. **Request Validation and Security**: Enhanced security with rate limiting and secret token validation
3. **Health Monitoring**: Health check and metrics endpoints for monitoring
4. **Concurrent Processing**: Improved concurrent request handling
5. **Error Handling**: Robust error handling and retry logic

## Python Implementation (bot/bot_run.py)

### Connection Pooling
- Uses aiohttp.TCPConnector with optimized settings:
  - Total connection pool size: 100
  - Per-host connection limit: 30
  - Keep-alive timeout: 30 seconds
  - DNS caching enabled

### Security Middleware
The `WebhookSecurityMiddleware` provides:
- Rate limiting (configurable requests per minute)
- Request validation
- Performance metrics tracking
- Secret token validation (if configured)

### Enhanced Webhook Server
- Uses aiohttp with SO_REUSEPORT for better performance
- Health check endpoint: `/health`
- Optional metrics endpoint: `/metrics`
- Proper graceful shutdown handling

## JavaScript Implementation (js/src/index.js)

### Enhanced Request Handling
- Content-type validation
- Secret token validation
- Asynchronous update processing for better throughput
- Response time headers
- Comprehensive error handling

### Health Monitoring
- Health check endpoint at `/health`
- Response time tracking
- Proper error logging

## Configuration

### Python (config.py)
```python
# Webhook performance and security settings
WEBHOOK_MAX_CONNECTIONS = 40  # Max simultaneous connections from Telegram
WEBHOOK_SECRET_TOKEN = ""  # Optional secret token for webhook validation
WEBHOOK_MAX_REQUESTS_PER_MINUTE = 100  # Rate limiting per user
WEBHOOK_METRICS_ENABLED = False  # Enable metrics endpoint at /metrics

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
```

### JavaScript (.env)
```bash
# Webhook performance and security settings
WEBHOOK_SECRET_TOKEN=
WEBHOOK_MAX_CONNECTIONS=40
```

## Testing

### Python Tests
Run webhook tests with:
```bash
python -m pytest tests/test_webhook.py -v
```

Tests cover:
- Webhook metrics functionality
- Rate limiting
- Security middleware
- Connection pooling
- Concurrent request handling
- Memory management

### JavaScript Tests
Run webhook tests with:
```bash
cd js && bun test tests/test_webhook.js
```

Tests cover:
- Health check endpoint
- Content type validation
- Secret token validation
- Malformed JSON handling
- Response time headers
- Concurrent request handling
- Configuration validation

## Performance Improvements

### Throughput Enhancements
1. **Connection Reuse**: HTTP keep-alive and connection pooling reduce connection overhead
2. **Asynchronous Processing**: Non-blocking request handling allows higher concurrency
3. **Rate Limiting**: Prevents abuse while maintaining legitimate traffic flow
4. **Optimized Error Handling**: Fast error responses prevent resource consumption

### Resource Optimization
1. **Memory Management**: Limited response time tracking prevents memory leaks
2. **DNS Caching**: Reduces DNS lookup overhead
3. **Connection Limits**: Prevents resource exhaustion under high load

### Security Benefits
1. **Request Validation**: Early rejection of invalid requests saves processing time
2. **Secret Token**: Validates requests are from Telegram
3. **Rate Limiting**: Protects against abuse and DoS attacks

## Monitoring and Metrics

### Health Check
Both implementations provide a `/health` endpoint that returns:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "webhook_url": "https://your.domain.com/webhook"
}
```

### Metrics (Python only)
When `WEBHOOK_METRICS_ENABLED=True`, the `/metrics` endpoint provides:
```json
{
  "request_count": 1000,
  "error_count": 5,
  "avg_response_time": 0.025,
  "error_rate": 0.005,
  "rate_limit_hits": 2,
  "last_reset": 1234567890
}
```

## Deployment Considerations

### Production Settings
For production deployments:
1. Set `WEBHOOK_SECRET_TOKEN` to a secure random string
2. Configure `WEBHOOK_MAX_CONNECTIONS` based on your server capacity
3. Enable metrics monitoring if needed
4. Use HTTPS for webhook URLs
5. Set appropriate rate limits

### Scaling
The optimizations support horizontal scaling:
- Stateless request processing
- Connection pooling per instance
- Health checks for load balancer integration

## Migration Guide

### From Basic Webhook Setup
No breaking changes - existing webhook configurations will continue to work with additional optimizations automatically enabled.

### New Configuration Options
Add these optional settings to your config for enhanced functionality:
- `WEBHOOK_SECRET_TOKEN`: For additional security
- `WEBHOOK_MAX_CONNECTIONS`: To optimize connection handling
- `WEBHOOK_METRICS_ENABLED`: For monitoring
- `WEBHOOK_MAX_REQUESTS_PER_MINUTE`: For rate limiting

## Troubleshooting

### Common Issues
1. **High Memory Usage**: Check if metrics are accumulating - they reset every hour
2. **Rate Limiting**: Adjust `WEBHOOK_MAX_REQUESTS_PER_MINUTE` if legitimate users are being limited
3. **Connection Issues**: Verify `WEBHOOK_MAX_CONNECTIONS` doesn't exceed server limits

### Debug Logging
Enable debug logging with `LOG_LEVEL="DEBUG"` to see detailed webhook processing information.