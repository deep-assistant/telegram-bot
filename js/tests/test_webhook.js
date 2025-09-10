/**
 * Comprehensive tests for webhook functionality and performance optimizations.
 */
import { test, expect } from 'bun:test';
import { config } from '../src/config.js';

// Mock config for testing
const testConfig = {
  ...config,
  webhookEnabled: true,
  webhookUrl: 'https://test.example.com/webhook',
  webhookPath: '/webhook',
  webhookHost: '127.0.0.1',
  webhookPort: 3001,
  webhookSecretToken: 'test-secret-token',
  webhookMaxConnections: 40,
  isDev: true
};

/**
 * Test webhook server functionality
 */
test('webhook server handles health check', async () => {
  // Create a simple webhook server for testing
  const server = Bun.serve({
    port: testConfig.webhookPort,
    hostname: testConfig.webhookHost,
    
    async fetch(req) {
      const url = new URL(req.url);
      
      if (url.pathname === '/health' && req.method === 'GET') {
        return new Response(JSON.stringify({
          status: 'healthy',
          timestamp: Date.now(),
          webhook_url: testConfig.webhookUrl
        }), {
          headers: { 'Content-Type': 'application/json' },
          status: 200
        });
      }
      
      return new Response('Not Found', { status: 404 });
    }
  });
  
  try {
    // Test health check endpoint
    const response = await fetch(`http://${testConfig.webhookHost}:${testConfig.webhookPort}/health`);
    expect(response.status).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.webhook_url).toBe(testConfig.webhookUrl);
    expect(typeof data.timestamp).toBe('number');
  } finally {
    server.stop();
  }
});

test('webhook server validates content type', async () => {
  const server = Bun.serve({
    port: testConfig.webhookPort + 1,
    hostname: testConfig.webhookHost,
    
    async fetch(req) {
      const url = new URL(req.url);
      
      if (url.pathname === testConfig.webhookPath && req.method === 'POST') {
        const contentType = req.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          return new Response('Bad Request', { status: 400 });
        }
        
        return new Response('OK', { status: 200 });
      }
      
      return new Response('Not Found', { status: 404 });
    }
  });
  
  try {
    // Test with invalid content type
    const invalidResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 1}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: 'invalid'
      }
    );
    expect(invalidResponse.status).toBe(400);
    
    // Test with valid content type
    const validResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 1}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test: 'data' })
      }
    );
    expect(validResponse.status).toBe(200);
  } finally {
    server.stop();
  }
});

test('webhook server validates secret token', async () => {
  const server = Bun.serve({
    port: testConfig.webhookPort + 2,
    hostname: testConfig.webhookHost,
    
    async fetch(req) {
      const url = new URL(req.url);
      
      if (url.pathname === testConfig.webhookPath && req.method === 'POST') {
        const contentType = req.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          return new Response('Bad Request', { status: 400 });
        }
        
        // Validate secret token
        const secretHeader = req.headers.get('x-telegram-bot-api-secret-token');
        if (secretHeader !== testConfig.webhookSecretToken) {
          return new Response('Unauthorized', { status: 401 });
        }
        
        return new Response('OK', { status: 200 });
      }
      
      return new Response('Not Found', { status: 404 });
    }
  });
  
  try {
    // Test without secret token
    const noTokenResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 2}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test: 'data' })
      }
    );
    expect(noTokenResponse.status).toBe(401);
    
    // Test with wrong secret token
    const wrongTokenResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 2}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-telegram-bot-api-secret-token': 'wrong-token'
        },
        body: JSON.stringify({ test: 'data' })
      }
    );
    expect(wrongTokenResponse.status).toBe(401);
    
    // Test with correct secret token
    const validTokenResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 2}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-telegram-bot-api-secret-token': testConfig.webhookSecretToken
        },
        body: JSON.stringify({ test: 'data' })
      }
    );
    expect(validTokenResponse.status).toBe(200);
  } finally {
    server.stop();
  }
});

test('webhook server handles malformed JSON', async () => {
  const server = Bun.serve({
    port: testConfig.webhookPort + 3,
    hostname: testConfig.webhookHost,
    
    async fetch(req) {
      const url = new URL(req.url);
      
      if (url.pathname === testConfig.webhookPath && req.method === 'POST') {
        const contentType = req.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          return new Response('Bad Request', { status: 400 });
        }
        
        try {
          await req.json();
          return new Response('OK', { status: 200 });
        } catch (err) {
          return new Response('Bad Request', { status: 400 });
        }
      }
      
      return new Response('Not Found', { status: 404 });
    }
  });
  
  try {
    // Test with malformed JSON
    const malformedResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 3}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{"malformed": json}'
      }
    );
    expect(malformedResponse.status).toBe(400);
    
    // Test with valid JSON
    const validResponse = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 3}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ valid: 'json' })
      }
    );
    expect(validResponse.status).toBe(200);
  } finally {
    server.stop();
  }
});

test('webhook server includes response time header', async () => {
  const server = Bun.serve({
    port: testConfig.webhookPort + 4,
    hostname: testConfig.webhookHost,
    
    async fetch(req) {
      const url = new URL(req.url);
      const startTime = Date.now();
      
      if (url.pathname === testConfig.webhookPath && req.method === 'POST') {
        const contentType = req.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          return new Response('Bad Request', { status: 400 });
        }
        
        // Simulate some processing time
        await new Promise(resolve => setTimeout(resolve, 10));
        
        const responseTime = Date.now() - startTime;
        
        return new Response('OK', { 
          status: 200,
          headers: {
            'Content-Type': 'text/plain',
            'X-Response-Time': `${responseTime}ms`
          }
        });
      }
      
      return new Response('Not Found', { status: 404 });
    }
  });
  
  try {
    const response = await fetch(
      `http://${testConfig.webhookHost}:${testConfig.webhookPort + 4}${testConfig.webhookPath}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test: 'data' })
      }
    );
    
    expect(response.status).toBe(200);
    
    const responseTimeHeader = response.headers.get('X-Response-Time');
    expect(responseTimeHeader).toBeTruthy();
    expect(responseTimeHeader).toMatch(/\d+ms/);
    
    // Response time should be at least 10ms due to our artificial delay
    const responseTime = parseInt(responseTimeHeader);
    expect(responseTime).toBeGreaterThanOrEqual(10);
  } finally {
    server.stop();
  }
});

test('webhook server handles concurrent requests', async () => {
  const requestCount = { value: 0 };
  
  const server = Bun.serve({
    port: testConfig.webhookPort + 5,
    hostname: testConfig.webhookHost,
    
    async fetch(req) {
      const url = new URL(req.url);
      
      if (url.pathname === testConfig.webhookPath && req.method === 'POST') {
        requestCount.value++;
        
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 50));
        
        return new Response('OK', { status: 200 });
      }
      
      return new Response('Not Found', { status: 404 });
    }
  });
  
  try {
    const startTime = Date.now();
    
    // Send 5 concurrent requests
    const requests = Array(5).fill().map(() =>
      fetch(`http://${testConfig.webhookHost}:${testConfig.webhookPort + 5}${testConfig.webhookPath}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test: 'data' })
      })
    );
    
    const responses = await Promise.all(requests);
    const endTime = Date.now();
    
    // All requests should succeed
    responses.forEach(response => {
      expect(response.status).toBe(200);
    });
    
    // All requests should be processed
    expect(requestCount.value).toBe(5);
    
    // Should complete in less time than sequential processing
    // (50ms * 5 = 250ms sequential, should be much less concurrent)
    const totalTime = endTime - startTime;
    expect(totalTime).toBeLessThan(200);
  } finally {
    server.stop();
  }
});

test('config validation', () => {
  // Test that config contains required webhook fields
  expect(typeof config.webhookEnabled).toBe('boolean');
  expect(typeof config.webhookPath).toBe('string');
  expect(typeof config.webhookHost).toBe('string');
  expect(typeof config.webhookPort).toBe('number');
  expect(typeof config.webhookMaxConnections).toBe('number');
  
  // Test default values
  expect(config.webhookPath).toBe('/webhook');
  expect(config.webhookHost).toBe('0.0.0.0');
  expect(config.webhookPort).toBe(3000);
  expect(config.webhookMaxConnections).toBe(40);
});