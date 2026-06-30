import Fastify from 'fastify';
import { createLogger } from '@cyberintel/shared';
import { Pool } from 'pg';
import neo4j from 'neo4j-driver';
import Redis from 'ioredis';
import { Client } from '@elastic/elasticsearch';

const logger = createLogger({ service: 'backend' });

const PORT = parseInt(process.env.BACKEND_PORT || '8001');

async function start() {
  const fastify = Fastify({ logger: false });

  // Database connections
  const pgPool = new Pool({
    connectionString: process.env.DATABASE_URL,
  });

  if (!process.env.NEO4J_PASSWORD) {
    throw new Error('NEO4J_PASSWORD environment variable is not set');
  }

  const neo4jDriver = neo4j.driver(
    process.env.NEO4J_URI || 'bolt://localhost:7687',
    neo4j.auth.basic(process.env.NEO4J_USER || 'neo4j', process.env.NEO4J_PASSWORD)
  );

  const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

  const elasticsearch = new Client({
    node: process.env.ELASTICSEARCH_URL || 'http://localhost:9200',
  });

  // Decorate fastify with database clients
  fastify.decorate('pg', pgPool);
  fastify.decorate('neo4j', neo4jDriver);
  fastify.decorate('redis', redis);
  fastify.decorate('elasticsearch', elasticsearch);

  // Health check
  fastify.get('/health', async () => {
    return { status: 'healthy', timestamp: new Date().toISOString() };
  });

  // Analytics endpoints
  fastify.get('/api/analytics/overview', async () => {
    try {
      const result = await pgPool.query(`
        SELECT 
          COUNT(DISTINCT id) as total_scans,
          COUNT(DISTINCT CASE WHEN status = 'COMPLETED' THEN id END) as completed_scans,
          COUNT(DISTINCT CASE WHEN status = 'RUNNING' THEN id END) as running_scans,
          COUNT(DISTINCT CASE WHEN status = 'FAILED' THEN id END) as failed_scans
        FROM scans
      `);

      return result.rows[0];
    } catch (error) {
      logger.error('Failed to get analytics', error);
      throw error;
    }
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

  // Start server
  await fastify.listen({ port: PORT, host: '0.0.0.0' });
  logger.info(`Backend listening on port ${PORT}`);

  // Graceful shutdown
  const shutdown = async () => {
    logger.info('Shutting down backend...');
    await pgPool.end();
    await neo4jDriver.close();
    await redis.quit();
    await fastify.close();
    process.exit(0);
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

start();
