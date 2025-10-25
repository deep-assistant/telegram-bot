import { config } from '../config.js';

// Simple logger for testing
const log = {
  debug: (...args) => console.log('[DEBUG]', ...args),
  info: (...args) => console.log('[INFO]', ...args),
  warn: (...args) => console.warn('[WARN]', ...args),
  error: (...args) => console.error('[ERROR]', ...args)
};

// API endpoints configuration with priority levels and capabilities
const API_ENDPOINTS = {
  primary: {
    url: config.proxyUrl,
    priority: 1,
    healthScore: 100,
    lastChecked: Date.now(),
    capabilities: {
      claude: true,
      gpt: true,
      llama: true,
      deepseek: true,
      o1: true,
      multimodal: true,
      streaming: true
    },
    rateLimits: {
      requestsPerMinute: 60,
      tokensPerMinute: 100000
    },
    currentUsage: {
      requests: 0,
      tokens: 0,
      lastReset: Date.now()
    }
  },
  deepinfra: {
    url: 'https://api.deepinfra.com/v1/openai',
    priority: 2,
    healthScore: 95,
    lastChecked: Date.now(),
    capabilities: {
      claude: false,
      gpt: false,
      llama: true,
      deepseek: true,
      o1: false,
      multimodal: true,
      streaming: true
    },
    rateLimits: {
      requestsPerMinute: 30,
      tokensPerMinute: 50000
    },
    currentUsage: {
      requests: 0,
      tokens: 0,
      lastReset: Date.now()
    }
  },
  goapi: {
    url: 'https://api.goapi.xyz/api/chatgpt/v1',
    priority: 3,
    healthScore: 90,
    lastChecked: Date.now(),
    capabilities: {
      claude: false,
      gpt: true,
      llama: false,
      deepseek: false,
      o1: false,
      multimodal: true,
      streaming: true
    },
    rateLimits: {
      requestsPerMinute: 20,
      tokensPerMinute: 30000
    },
    currentUsage: {
      requests: 0,
      tokens: 0,
      lastReset: Date.now()
    }
  }
};

// Model to API provider mapping
const MODEL_PROVIDERS = {
  'claude-3-opus': ['primary'],
  'claude-3-5-sonnet': ['primary'],
  'claude-3-5-haiku': ['primary'],
  'claude-3-7-sonnet': ['primary'],
  'gpt-4o': ['primary', 'goapi'],
  'gpt-4o-mini': ['primary', 'goapi'],
  'gpt-4o-unofficial': ['goapi'],
  'gpt-3.5-turbo': ['primary', 'goapi'],
  'gpt-auto': ['primary', 'goapi'],
  'o1-mini': ['primary'],
  'o1-preview': ['primary'],
  'o3-mini': ['primary'],
  'meta-llama/Meta-Llama-3.1-405B': ['primary', 'deepinfra'],
  'meta-llama/Meta-Llama-3.1-70B': ['primary', 'deepinfra'],
  'meta-llama/Meta-Llama-3.1-8B': ['primary', 'deepinfra'],
  'meta-llama/Meta-Llama-3-70B-Instruct': ['primary', 'deepinfra'],
  'deepseek-chat': ['primary', 'deepinfra'],
  'deepseek-reasoner': ['primary', 'deepinfra'],
  'uncensored': ['primary']
};

class ApiPriorityService {
  constructor() {
    this.endpoints = { ...API_ENDPOINTS };
    this.failureHistory = new Map(); // Track recent failures
    this.responseTimeHistory = new Map(); // Track response times
    this.healthCheckInterval = null;
    // Don't start health checks immediately for testing
  }

  /**
   * Get the best API endpoint for a specific model
   * @param {string} model - The model identifier
   * @param {Object} requestContext - Additional context (user, request type, etc.)
   * @returns {Object} Best API endpoint configuration
   */
  getBestApiForModel(model, requestContext = {}) {
    const availableProviders = MODEL_PROVIDERS[model] || ['primary'];
    const candidates = availableProviders
      .map(providerId => ({
        id: providerId,
        ...this.endpoints[providerId]
      }))
      .filter(provider => this.isProviderHealthy(provider))
      .sort((a, b) => this.calculateScore(a, model, requestContext) - this.calculateScore(b, model, requestContext));

    if (candidates.length === 0) {
      log.warn(`No healthy providers available for model ${model}, falling back to primary`);
      return {
        id: 'primary',
        ...this.endpoints.primary
      };
    }

    const bestProvider = candidates[0];
    log.debug(`Selected provider ${bestProvider.id} for model ${model} with score ${this.calculateScore(bestProvider, model, requestContext)}`);
    
    return bestProvider;
  }

  /**
   * Calculate priority score for an API provider (lower is better)
   * @param {Object} provider - Provider configuration
   * @param {string} model - Model being requested
   * @param {Object} context - Request context
   * @returns {number} Priority score
   */
  calculateScore(provider, model, context) {
    let score = provider.priority * 10; // Base priority

    // Health score factor (lower health = higher score/worse)
    score += (100 - provider.healthScore) * 0.5;

    // Rate limiting factor
    const rateLimitPenalty = this.getRateLimitPenalty(provider);
    score += rateLimitPenalty * 20;

    // Response time factor
    const avgResponseTime = this.getAverageResponseTime(provider.id);
    score += avgResponseTime * 0.01; // Convert ms to score points

    // Recent failures penalty
    const failurePenalty = this.getFailurePenalty(provider.id);
    score += failurePenalty * 50;

    // Model compatibility bonus
    if (this.hasModelCompatibility(provider, model)) {
      score -= 5; // Bonus for supporting the model
    }

    // Multimodal capability bonus for image/video requests
    if (context.hasMedia && provider.capabilities.multimodal) {
      score -= 10;
    }

    return score;
  }

  /**
   * Check if provider is currently healthy
   * @param {Object} provider - Provider configuration
   * @returns {boolean} True if healthy
   */
  isProviderHealthy(provider) {
    return provider.healthScore > 50 && !this.isRateLimited(provider);
  }

  /**
   * Check if provider has hit rate limits
   * @param {Object} provider - Provider configuration
   * @returns {boolean} True if rate limited
   */
  isRateLimited(provider) {
    const now = Date.now();
    const minutesSinceReset = (now - provider.currentUsage.lastReset) / (1000 * 60);

    if (minutesSinceReset >= 1) {
      // Reset usage counters
      provider.currentUsage.requests = 0;
      provider.currentUsage.tokens = 0;
      provider.currentUsage.lastReset = now;
      return false;
    }

    return (
      provider.currentUsage.requests >= provider.rateLimits.requestsPerMinute ||
      provider.currentUsage.tokens >= provider.rateLimits.tokensPerMinute
    );
  }

  /**
   * Get rate limit penalty score
   * @param {Object} provider - Provider configuration
   * @returns {number} Penalty score (0-1)
   */
  getRateLimitPenalty(provider) {
    const requestUsage = provider.currentUsage.requests / provider.rateLimits.requestsPerMinute;
    const tokenUsage = provider.currentUsage.tokens / provider.rateLimits.tokensPerMinute;
    return Math.max(requestUsage, tokenUsage);
  }

  /**
   * Get average response time for a provider
   * @param {string} providerId - Provider identifier
   * @returns {number} Average response time in ms
   */
  getAverageResponseTime(providerId) {
    const history = this.responseTimeHistory.get(providerId) || [];
    if (history.length === 0) return 1000; // Default 1s
    return history.reduce((sum, time) => sum + time, 0) / history.length;
  }

  /**
   * Get failure penalty for a provider
   * @param {string} providerId - Provider identifier
   * @returns {number} Failure penalty (0-1)
   */
  getFailurePenalty(providerId) {
    const failures = this.failureHistory.get(providerId) || [];
    const recentFailures = failures.filter(time => Date.now() - time < 300000); // Last 5 minutes
    return Math.min(recentFailures.length / 5, 1); // Max penalty at 5 failures
  }

  /**
   * Check if provider has compatibility with model
   * @param {Object} provider - Provider configuration
   * @param {string} model - Model identifier
   * @returns {boolean} True if compatible
   */
  hasModelCompatibility(provider, model) {
    if (model.includes('claude')) return provider.capabilities.claude;
    if (model.includes('gpt')) return provider.capabilities.gpt;
    if (model.includes('llama')) return provider.capabilities.llama;
    if (model.includes('deepseek')) return provider.capabilities.deepseek;
    if (model.includes('o1') || model.includes('o3')) return provider.capabilities.o1;
    return true; // Default compatibility
  }

  /**
   * Record a successful request
   * @param {string} providerId - Provider identifier
   * @param {number} responseTime - Response time in ms
   * @param {number} tokensUsed - Number of tokens used
   */
  recordSuccess(providerId, responseTime, tokensUsed = 0) {
    const provider = this.endpoints[providerId];
    if (!provider) return;

    // Update usage counters
    provider.currentUsage.requests++;
    provider.currentUsage.tokens += tokensUsed;

    // Record response time
    const history = this.responseTimeHistory.get(providerId) || [];
    history.push(responseTime);
    if (history.length > 10) history.shift(); // Keep last 10 measurements
    this.responseTimeHistory.set(providerId, history);

    // Improve health score on success
    provider.healthScore = Math.min(100, provider.healthScore + 1);

    log.debug(`Recorded success for ${providerId}: ${responseTime}ms, ${tokensUsed} tokens`);
  }

  /**
   * Record a failed request
   * @param {string} providerId - Provider identifier
   * @param {Error} error - The error that occurred
   */
  recordFailure(providerId, error) {
    const provider = this.endpoints[providerId];
    if (!provider) return;

    // Record failure time
    const failures = this.failureHistory.get(providerId) || [];
    failures.push(Date.now());
    if (failures.length > 10) failures.shift(); // Keep last 10 failures
    this.failureHistory.set(providerId, failures);

    // Decrease health score on failure
    provider.healthScore = Math.max(0, provider.healthScore - 10);

    log.warn(`Recorded failure for ${providerId}:`, error.message);
  }

  /**
   * Start periodic health checks
   */
  startHealthChecks() {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthChecks();
    }, 60000); // Check every minute
  }

  /**
   * Perform health checks on all endpoints
   */
  async performHealthChecks() {
    for (const [providerId, provider] of Object.entries(this.endpoints)) {
      try {
        const startTime = Date.now();
        
        // Perform a lightweight health check (implementation depends on API)
        // For now, we'll just check if the endpoint is reachable
        const response = await fetch(provider.url, {
          method: 'HEAD',
          timeout: 5000
        }).catch(() => null);

        const responseTime = Date.now() - startTime;

        if (response && response.ok) {
          provider.healthScore = Math.min(100, provider.healthScore + 2);
          this.recordSuccess(providerId, responseTime, 0);
        } else {
          provider.healthScore = Math.max(0, provider.healthScore - 5);
        }

        provider.lastChecked = Date.now();
      } catch (error) {
        this.recordFailure(providerId, error);
      }
    }
  }

  /**
   * Get current status of all providers
   * @returns {Object} Status information
   */
  getProviderStatus() {
    return Object.entries(this.endpoints).map(([id, provider]) => ({
      id,
      url: provider.url,
      priority: provider.priority,
      healthScore: provider.healthScore,
      lastChecked: provider.lastChecked,
      isHealthy: this.isProviderHealthy(provider),
      isRateLimited: this.isRateLimited(provider),
      avgResponseTime: this.getAverageResponseTime(id),
      recentFailures: (this.failureHistory.get(id) || []).filter(time => Date.now() - time < 300000).length
    }));
  }

  /**
   * Add or update an API endpoint
   * @param {string} id - Provider identifier
   * @param {Object} config - Provider configuration
   */
  addProvider(id, config) {
    this.endpoints[id] = {
      ...config,
      healthScore: config.healthScore || 100,
      lastChecked: Date.now(),
      currentUsage: {
        requests: 0,
        tokens: 0,
        lastReset: Date.now()
      }
    };
    log.info(`Added provider ${id}: ${config.url}`);
  }

  /**
   * Remove an API endpoint
   * @param {string} id - Provider identifier
   */
  removeProvider(id) {
    if (id === 'primary') {
      log.warn('Cannot remove primary provider');
      return false;
    }

    delete this.endpoints[id];
    this.failureHistory.delete(id);
    this.responseTimeHistory.delete(id);
    log.info(`Removed provider ${id}`);
    return true;
  }

  /**
   * Clean up resources
   */
  destroy() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }
}

export const apiPriorityService = new ApiPriorityService();