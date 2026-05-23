import Fastify from 'fastify';
import { createLogger } from '@cyberintel/shared';
import { AIRouter } from './router';
import { ProviderRegistry } from './providers/registry';
import { OllamaProvider } from './providers/ollama';
import { OpenAIProvider } from './providers/openai';
import { AnthropicProvider } from './providers/anthropic';
import { OpenRouterProvider } from './providers/openrouter';
import { GroqProvider } from './providers/groq';
import { DeepSeekProvider } from './providers/deepseek';
import Redis from 'ioredis';

const logger = createLogger({ service: 'ai-router' });

const PORT = parseInt(process.env.AI_ROUTER_PORT || '8003');

async function start() {
  const fastify = Fastify({ logger: false });

  const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

  // Initialize provider registry
  const registry = new ProviderRegistry();

  // Register providers
  if (process.env.OLLAMA_URL) {
    registry.register(new OllamaProvider(process.env.OLLAMA_URL));
  }
  if (process.env.OPENAI_API_KEY) {
    registry.register(new OpenAIProvider(process.env.OPENAI_API_KEY));
  }
  if (process.env.ANTHROPIC_API_KEY) {
    registry.register(new AnthropicProvider(process.env.ANTHROPIC_API_KEY));
  }
  if (process.env.OPENROUTER_API_KEY) {
    registry.register(new OpenRouterProvider(process.env.OPENROUTER_API_KEY));
  }
  if (process.env.GROQ_API_KEY) {
    registry.register(new GroqProvider(process.env.GROQ_API_KEY));
  }
  if (process.env.DEEPSEEK_API_KEY) {
    registry.register(new DeepSeekProvider(process.env.DEEPSEEK_API_KEY));
  }

  const router = new AIRouter(registry, redis);

  // Chat completion endpoint
  fastify.post('/api/chat', async (request, reply) => {
    const { messages, provider, model, temperature, maxTokens, stream } = request.body as any;

    try {
      const response = await router.chat({
        messages,
        provider,
        model,
        temperature,
        maxTokens,
        stream,
      });

      return response;
    } catch (error) {
      logger.error('Chat completion failed', error);
      return reply.code(500).send({
        error: {
          message: 'Chat completion failed',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      });
    }
  });

  // Streaming chat endpoint
  fastify.post('/api/chat/stream', async (request, reply) => {
    const { messages, provider, model, temperature, maxTokens } = request.body as any;

    reply.raw.setHeader('Content-Type', 'text/event-stream');
    reply.raw.setHeader('Cache-Control', 'no-cache');
    reply.raw.setHeader('Connection', 'keep-alive');

    try {
      const stream = await router.chatStream({
        messages,
        provider,
        model,
        temperature,
        maxTokens,
      });

      for await (const chunk of stream) {
        reply.raw.write(`data: ${JSON.stringify(chunk)}\n\n`);
      }

      reply.raw.end();
    } catch (error) {
      logger.error('Streaming chat failed', error);
      reply.raw.write(`data: ${JSON.stringify({ error: 'Stream failed' })}\n\n`);
      reply.raw.end();
    }
  });

  // Get available providers
  fastify.get('/api/providers', async () => {
    return { providers: registry.listProviders() };
  });

  // Get provider stats
  fastify.get('/api/stats', async () => {
    const stats = await router.getStats();
    return stats;
  });

  // Health check
  fastify.get('/health', async () => {
    const redisHealthy = redis.status === 'ready';
    const providers = registry.getAvailableProviders();
    
    return {
      status: redisHealthy && providers.length > 0 ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      service: 'ai-router',
      version: '1.0.0',
      uptime: process.uptime(),
      dependencies: {
        redis: redisHealthy ? 'up' : 'down',
      },
      providers: providers.map(p => ({
        name: p.name,
        healthy: p.healthy,
      })),
    };
  });

  // Global error handler
  fastify.setErrorHandler((error, request, reply) => {
    logger.error('Unhandled error', error, {
      path: request.url,
      method: request.method,
    });

    const statusCode = error.statusCode || 500;
    reply.status(statusCode).send({
      error: {
        message: statusCode === 500 ? 'Internal server error' : error.message,
        code: error.code || 'INTERNAL_ERROR',
      },
    });
  });

  await fastify.listen({ port: PORT, host: '0.0.0.0' });
  logger.info(`AI Router listening on port ${PORT}`);

  // Graceful shutdown
  const shutdown = async () => {
    logger.info('Shutting down AI router...');
    await fastify.close();
    await redis.quit();
    process.exit(0);
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

start();
