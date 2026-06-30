import Fastify from 'fastify';
import neo4j from 'neo4j-driver';
import { createLogger } from '@cyberintel/shared';
import { GraphService } from './service';

const logger = createLogger({ service: 'graph-engine' });

const PORT = parseInt(process.env.GRAPH_ENGINE_PORT || '8004');

async function start() {
  const fastify = Fastify({ logger: false });

  // Neo4j connection
  const driver = neo4j.driver(
    process.env.NEO4J_URI || 'bolt://localhost:7687',
    neo4j.auth.basic(process.env.NEO4J_USER || 'neo4j', process.env.NEO4J_PASSWORD || 'cyberintel')
  );

  const graphService = new GraphService(driver);

  // Create node
  fastify.post('/api/nodes', async (request, reply) => {
    try {
      const { label, properties } = request.body as any;
      const node = await graphService.createNode(label, properties);
      return node;
    } catch (error) {
      logger.error('Failed to create node', error);
      throw error;
    }
  });

  // Create relationship
  fastify.post('/api/relationships', async (request, reply) => {
    try {
      const { sourceId, targetId, type, properties } = request.body as any;
      const rel = await graphService.createRelationship(sourceId, targetId, type, properties);
      return rel;
    } catch (error) {
      logger.error('Failed to create relationship', error);
      throw error;
    }
  });

  // Query graph
  fastify.post('/api/query', async (request, reply) => {
    try {
      const { cypher, params } = request.body as any;
      const result = await graphService.query(cypher, params);
      return result;
    } catch (error) {
      logger.error('Failed to query graph', error);
      throw error;
    }
  });

  // Get neighbors
  fastify.get('/api/nodes/:nodeId/neighbors', async (request, reply) => {
    const { nodeId } = request.params as { nodeId: string };
    const { depth = 1 } = request.query as any;
    const neighbors = await graphService.getNeighbors(nodeId, depth);
    return neighbors;
  });

  // Find paths
  fastify.post('/api/paths', async (request, reply) => {
    const { sourceId, targetId, maxDepth = 5 } = request.body as any;
    const paths = await graphService.findPaths(sourceId, targetId, maxDepth);
    return paths;
  });

  // Health check
  fastify.get('/health', async () => {
    let neo4jHealthy = false;
    try {
      await driver.verifyConnectivity();
      neo4jHealthy = true;
    } catch (error) {
      logger.error('Neo4j health check failed', error);
    }

    return {
      status: neo4jHealthy ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      service: 'graph-engine',
      version: '1.0.0',
      uptime: process.uptime(),
      dependencies: {
        neo4j: neo4jHealthy ? 'up' : 'down',
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
  logger.info(`Graph Engine listening on port ${PORT}`);

  // Graceful shutdown
  const shutdown = async () => {
    logger.info('Shutting down graph engine...');
    await driver.close();
    await fastify.close();
    process.exit(0);
  };

  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

start();
