import Fastify from 'fastify';
import { createLogger, AgentType, TaskStatus } from '@cyberintel/shared';
import { TaskQueue } from './queue';
import { TaskScheduler } from './scheduler';
import { WorkflowEngine } from './workflow';
import Redis from 'ioredis';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger({ service: 'orchestrator' });

const PORT = parseInt(process.env.ORCHESTRATOR_PORT || '8002');

async function start() {
  const fastify = Fastify({ logger: false });

  const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
  const queue = new TaskQueue(redis);
  const scheduler = new TaskScheduler(queue);
  const workflow = new WorkflowEngine(queue, scheduler);

  // Health check
  fastify.get('/health', async () => {
    const redisHealthy = redis.status === 'ready';

    return {
      status: redisHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      service: 'orchestrator',
      version: '1.0.0',
      uptime: process.uptime(),
      dependencies: {
        redis: redisHealthy ? 'up' : 'down',
      },
    };
  });

  // Create scan workflow
  fastify.post('/api/tasks', async (request, reply) => {
    const { scanId, target, targetType, modules, depth, autoRecon } = request.body as any;

    logger.info('Creating scan workflow', { scanId, target });

    try {
      // Create workflow
      const workflowId = await workflow.createScanWorkflow({
        scanId,
        target,
        targetType,
        modules,
        depth,
        autoRecon,
      });

      return { workflowId, scanId, status: 'started' };
    } catch (error) {
      logger.error('Failed to create workflow', error);
      throw error;
    }
  });

  // Get task status
  fastify.get('/api/tasks/:taskId', async (request, reply) => {
    const { taskId } = request.params as { taskId: string };
    const task = await queue.getTask(taskId);

    if (!task) {
      return reply.code(404).send({ error: 'Task not found' });
    }

    return task;
  });

  // Cancel task
  fastify.post('/api/tasks/:taskId/cancel', async (request, reply) => {
    const { taskId } = request.params as { taskId: string };
    await queue.cancelTask(taskId);
    return { success: true };
  });

  // Get queue stats
  fastify.get('/api/stats', async () => {
    try {
      const stats = await queue.getStats();
      return stats;
    } catch (error) {
      logger.error('Failed to get stats', error);
      throw error;
    }
  });

  // Health check
  fastify.get('/health', async () => {
    const redisHealthy = redis.status === 'ready';

    return {
      status: redisHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      service: 'orchestrator',
      version: '1.0.0',
      uptime: process.uptime(),
      dependencies: {
        redis: redisHealthy ? 'up' : 'down',
      },
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
  logger.info(`Orchestrator listening on port ${PORT}`);

  // Start scheduler
  scheduler.start();

  // Graceful shutdown
  const shutdown = async () => {
    logger.info('Shutting down orchestrator...');
    scheduler.stop();
    await fastify.close();
    await redis.quit();
    process.exit(0);
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

start();
