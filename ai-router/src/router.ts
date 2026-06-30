import { createLogger } from '@cyberintel/shared';
import { ProviderRegistry } from './providers/registry';
import { AIProvider, ChatRequest, ChatResponse } from './providers/base';
import Redis from 'ioredis';

const logger = createLogger({ service: 'ai-router' });

export class AIRouter {
  private registry: ProviderRegistry;
  private redis: Redis;
  private defaultProvider: string;

  constructor(registry: ProviderRegistry, redis: Redis) {
    this.registry = registry;
    this.redis = redis;
    this.defaultProvider = process.env.DEFAULT_AI_PROVIDER || 'ollama';
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const providerName = request.provider || this.defaultProvider;

    try {
      const provider = this.registry.getProvider(providerName);

      if (!provider) {
        throw new Error(`Provider ${providerName} not available`);
      }

      logger.info('Routing chat request', { provider: providerName, model: request.model });

      const response = await provider.chat(request);

      // Track usage
      await this.trackUsage(providerName, request, response);

      return response;
    } catch (error) {
      logger.error('Chat request failed', error, { provider: providerName });

      // Fallback to next available provider
      if (!request.provider) {
        return this.chatWithFallback(request, [providerName]);
      }

      throw error;
    }
  }

  async chatStream(request: ChatRequest): AsyncGenerator<any> {
    const providerName = request.provider || this.defaultProvider;
    const provider = this.registry.getProvider(providerName);

    if (!provider) {
      throw new Error(`Provider ${providerName} not available`);
    }

    logger.info('Routing streaming chat request', { provider: providerName });

    return provider.chatStream(request);
  }

  private async chatWithFallback(
    request: ChatRequest,
    triedProviders: string[]
  ): Promise<ChatResponse> {
    const availableProviders = this.registry
      .listProviders()
      .filter((p) => !triedProviders.includes(p.name) && p.available);

    if (availableProviders.length === 0) {
      throw new Error('No available AI providers');
    }

    const nextProvider = availableProviders[0];
    logger.warn('Falling back to provider', { provider: nextProvider.name });

    try {
      const provider = this.registry.getProvider(nextProvider.name);
      if (!provider) throw new Error('Provider not found');

      const response = await provider.chat(request);
      await this.trackUsage(nextProvider.name, request, response);
      return response;
    } catch (error) {
      logger.error('Fallback provider failed', error, { provider: nextProvider.name });
      return this.chatWithFallback(request, [...triedProviders, nextProvider.name]);
    }
  }

  private async trackUsage(
    provider: string,
    request: ChatRequest,
    response: ChatResponse
  ): Promise<void> {
    const key = `ai:usage:${provider}:${new Date().toISOString().split('T')[0]}`;

    await this.redis.hincrby(key, 'requests', 1);
    await this.redis.hincrby(key, 'tokens', response.usage?.totalTokens || 0);
    await this.redis.expire(key, 86400 * 30); // 30 days
  }

  async getStats(): Promise<any> {
    const providers = this.registry.listProviders();
    const today = new Date().toISOString().split('T')[0];

    const stats = await Promise.all(
      providers.map(async (p) => {
        const key = `ai:usage:${p.name}:${today}`;
        const usage = await this.redis.hgetall(key);

        return {
          provider: p.name,
          available: p.available,
          requests: parseInt(usage.requests || '0'),
          tokens: parseInt(usage.tokens || '0'),
        };
      })
    );

    return { providers: stats };
  }
}
