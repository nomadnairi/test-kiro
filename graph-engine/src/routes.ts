import { FastifyInstance } from 'fastify';
import { GraphIntelligence } from './intelligence';

export async function registerIntelligenceRoutes(
  fastify: FastifyInstance,
  intelligence: GraphIntelligence
) {
  // Link entities
  fastify.post('/api/intelligence/link', async (request, reply) => {
    const { links } = request.body as any;
    await intelligence.linkEntities(links);
    return { success: true };
  });

  // Find infrastructure clusters
  fastify.get('/api/intelligence/clusters', async (request, reply) => {
    const clusters = await intelligence.findInfrastructureClusters();
    return { clusters };
  });

  // Find attack chains
  fastify.get('/api/intelligence/attack-chains/:nodeId', async (request, reply) => {
    const { nodeId } = request.params as { nodeId: string };
    const chains = await intelligence.findAttackChains(nodeId);
    return { chains };
  });

  // Calculate centrality
  fastify.get('/api/intelligence/centrality', async (request, reply) => {
    const { nodeType } = request.query as any;
    const centrality = await intelligence.calculateCentrality(nodeType);
    return { centrality };
  });

  // Find related breaches
  fastify.get('/api/intelligence/breaches/:entityId', async (request, reply) => {
    const { entityId } = request.params as { entityId: string };
    const breaches = await intelligence.findRelatedBreaches(entityId);
    return { breaches };
  });

  // Correlate IOCs
  fastify.get('/api/intelligence/ioc-correlation/:iocId', async (request, reply) => {
    const { iocId } = request.params as { iocId: string };
    const related = await intelligence.correlateIOCs(iocId);
    return { related };
  });

  // Build timeline
  fastify.get('/api/intelligence/timeline/:entityId', async (request, reply) => {
    const { entityId } = request.params as { entityId: string };
    const timeline = await intelligence.buildTimeline(entityId);
    return { timeline };
  });

  // Find actor clusters
  fastify.get('/api/intelligence/actor-clusters', async (request, reply) => {
    const clusters = await intelligence.findActorClusters();
    return { clusters };
  });

  // Score relationship
  fastify.post('/api/intelligence/score-relationship', async (request, reply) => {
    const { sourceId, targetId } = request.body as any;
    const score = await intelligence.scoreRelationship(sourceId, targetId);
    return { score };
  });
}
