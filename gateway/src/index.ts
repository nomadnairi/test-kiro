import Fastify from 'fastify';
import cors from '@fastify/cors';
import jwt from '@fastify/jwt';
import rateLimit from '@fastify/rate-limit';
import websocket from '@fastify/websocket';
import { createLogger } from '@cyberintel/shared';
import { authRoutes } from './routes/auth';
import { scanRoutes } from './routes/scans';
import { entityRoutes } from './routes/entities';
import { iocRoutes } from './routes/iocs';
import { userRoutes } from './routes/users';
import { wsHandler } from './websocket';
import { errorHandler } from './middleware/errorHandler';
import { authMiddleware } from './middleware/auth';
import Redis from 'ioredis';

const logger = createLogger({ service: 'gateway' });

const PORT = parseInt(process.env.GATEWAY_PORT || '8000');
const HOST = process.env.HOST || '0.0.0.0';

async function start() {
  const fastify = Fastify({
    logger: false,
    trustProxy: true,
  });

  // Redis connection
  const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
  fastify.decorate('redis', redis);

  // CORS
  await fastify.register(cors, {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true,
  });

  // JWT
  await fastify.register(jwt, {
    secret: process.env.JWT_SECRET || 'your-secret-key',
  });

  // Rate limiting
  await fastify.register(rateLimit, {
    max: parseInt(process.env.RATE_LIMIT_MAX || '100'),
    timeWindow: process.env.RATE_LIMIT_WINDOW || '15 minutes',
    redis,
  });

  // WebSocket
  await fastify.register(websocket);

  // Health check
  fastify.get('/health', async () => {
    return { status: 'healthy', timestamp: new Date().toISOString() };
  });

  // Auth routes (public)
  await fastify.register(authRoutes, { prefix: '/api/auth' });

  // Protected routes
  fastify.addHook('onRequest', authMiddleware);

  await fastify.register(scanRoutes, { prefix: '/api/scans' });
  await fastify.register(entityRoutes, { prefix: '/api/entities' });
  await fastify.register(iocRoutes, { prefix: '/api/iocs' });
  await fastify.register(userRoutes, { prefix: '/api/users' });

  // WebSocket endpoint
  fastify.register(async (fastify) => {
    fastify.get('/ws', { websocket: true }, wsHandler);
  });

  // Error handler
  fastify.setErrorHandler(errorHandler);

  // Error handler
  fastify.setErrorHandler(errorHandler);

  // Start server
  try {
    await fastify.listen({ port: PORT, host: HOST });
    logger.info(`Gateway listening on ${HOST}:${PORT}`);
  } catch (err) {
    logger.error('Failed to start gateway', err);
    process.exit(1);
  }

  // Graceful shutdown
  const shutdown = async () => {
    logger.info('Shutting down gateway...');
    await fastify.close();
    await redis.quit();
    process.exit(0);
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

start();
