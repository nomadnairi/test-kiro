import neo4j, { Driver } from 'neo4j-driver';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'graph-intelligence' });

export interface EntityLink {
  sourceId: string;
  targetId: string;
  type: string;
  confidence: number;
  properties?: Record<string, any>;
}

export interface InfrastructureCluster {
  id: string;
  entities: string[];
  type: string;
  confidence: number;
}

export interface AttackChain {
  id: string;
  nodes: string[];
  relationships: string[];
  severity: string;
}

export class GraphIntelligence {
  private driver: Driver;

  constructor(driver: Driver) {
    this.driver = driver;
  }

  async linkEntities(links: EntityLink[]): Promise<void> {
    const session = this.driver.session();
    
    try {
      for (const link of links) {
        await session.run(
          `MATCH (a {id: $sourceId}), (b {id: $targetId})
           MERGE (a)-[r:${link.type}]->(b)
           SET r.confidence = $confidence,
               r.properties = $properties,
               r.created_at = datetime()`,
          {
            sourceId: link.sourceId,
            targetId: link.targetId,
            confidence: link.confidence,
            properties: link.properties || {},
          }
        );
      }

      logger.info('Entities linked', { count: links.length });
    } finally {
      await session.close();
    }
  }

  async findInfrastructureClusters(): Promise<InfrastructureCluster[]> {
    const session = this.driver.session();
    
    try {
      // Find clusters of related infrastructure
      const result = await session.run(`
        CALL gds.louvain.stream('infrastructure-graph')
        YIELD nodeId, communityId
        WITH communityId, collect(gds.util.asNode(nodeId).id) as members
        WHERE size(members) > 2
        RETURN communityId, members
        ORDER BY size(members) DESC
        LIMIT 20
      `);

      const clusters: InfrastructureCluster[] = result.records.map((record, index) => ({
        id: `cluster-${index}`,
        entities: record.get('members'),
        type: 'infrastructure',
        confidence: 0.8,
      }));

      logger.info('Infrastructure clusters found', { count: clusters.length });
      return clusters;
    } catch (error) {
      logger.error('Failed to find clusters', error);
      return [];
    } finally {
      await session.close();
    }
  }

  async findAttackChains(startNodeId: string): Promise<AttackChain[]> {
    const session = this.driver.session();
    
    try {
      // Find potential attack chains
      const result = await session.run(`
        MATCH path = (start {id: $startNodeId})-[*1..5]->(end)
        WHERE end:VULNERABILITY OR end:EXPOSED_SERVICE
        RETURN path
        LIMIT 10
      `, { startNodeId });

      const chains: AttackChain[] = result.records.map((record, index) => {
        const path = record.get('path');
        const nodes = path.segments.map((seg: any) => seg.start.properties.id);
        const relationships = path.segments.map((seg: any) => seg.relationship.type);

        return {
          id: `chain-${index}`,
          nodes,
          relationships,
          severity: this.calculateChainSeverity(path),
        };
      });

      logger.info('Attack chains found', { count: chains.length });
      return chains;
    } finally {
      await session.close();
    }
  }

  async calculateCentrality(nodeType?: string): Promise<Record<string, number>> {
    const session = this.driver.session();
    
    try {
      const typeFilter = nodeType ? `WHERE n:${nodeType}` : '';
      
      const result = await session.run(`
        MATCH (n)
        ${typeFilter}
        WITH n, size((n)--()) as degree
        RETURN n.id as nodeId, degree
        ORDER BY degree DESC
        LIMIT 100
      `);

      const centrality: Record<string, number> = {};
      result.records.forEach(record => {
        centrality[record.get('nodeId')] = record.get('degree');
      });

      logger.info('Centrality calculated', { nodes: Object.keys(centrality).length });
      return centrality;
    } finally {
      await session.close();
    }
  }

  async findRelatedBreaches(entityId: string): Promise<any[]> {
    const session = this.driver.session();
    
    try {
      const result = await session.run(`
        MATCH (e {id: $entityId})-[:EXPOSED_IN|FOUND_IN*1..2]-(b:BREACH)
        RETURN DISTINCT b
        ORDER BY b.date DESC
        LIMIT 20
      `, { entityId });

      const breaches = result.records.map(record => {
        const breach = record.get('b').properties;
        return {
          id: breach.id,
          name: breach.name,
          date: breach.date,
          records: breach.records,
          dataTypes: breach.dataTypes,
        };
      });

      logger.info('Related breaches found', { count: breaches.length });
      return breaches;
    } finally {
      await session.close();
    }
  }

  async correlateIOCs(iocId: string): Promise<any[]> {
    const session = this.driver.session();
    
    try {
      const result = await session.run(`
        MATCH (ioc:IOC {id: $iocId})-[r*1..3]-(related)
        WHERE related:IOC OR related:THREAT_ACTOR OR related:CAMPAIGN
        RETURN DISTINCT related, type(r[0]) as relationshipType
        LIMIT 50
      `, { iocId });

      const related = result.records.map(record => ({
        entity: record.get('related').properties,
        relationship: record.get('relationshipType'),
      }));

      logger.info('IOCs correlated', { count: related.length });
      return related;
    } finally {
      await session.close();
    }
  }

  async buildTimeline(entityId: string): Promise<any[]> {
    const session = this.driver.session();
    
    try {
      const result = await session.run(`
        MATCH (e {id: $entityId})-[r]-(related)
        WHERE r.timestamp IS NOT NULL
        RETURN related, r, r.timestamp as timestamp
        ORDER BY timestamp DESC
        LIMIT 100
      `, { entityId });

      const timeline = result.records.map(record => ({
        timestamp: record.get('timestamp'),
        entity: record.get('related').properties,
        relationship: record.get('r').type,
      }));

      logger.info('Timeline built', { events: timeline.length });
      return timeline;
    } finally {
      await session.close();
    }
  }

  async findActorClusters(): Promise<any[]> {
    const session = this.driver.session();
    
    try {
      const result = await session.run(`
        MATCH (actor:THREAT_ACTOR)-[:USES|TARGETS*1..2]-(entity)
        WITH actor, collect(DISTINCT entity) as relatedEntities
        WHERE size(relatedEntities) > 3
        RETURN actor, relatedEntities
        ORDER BY size(relatedEntities) DESC
        LIMIT 20
      `);

      const clusters = result.records.map(record => ({
        actor: record.get('actor').properties,
        relatedEntities: record.get('relatedEntities').map((e: any) => e.properties),
      }));

      logger.info('Actor clusters found', { count: clusters.length });
      return clusters;
    } finally {
      await session.close();
    }
  }

  async scoreRelationship(sourceId: string, targetId: string): Promise<number> {
    const session = this.driver.session();
    
    try {
      // Calculate relationship confidence based on multiple factors
      const result = await session.run(`
        MATCH (a {id: $sourceId})-[r]-(b {id: $targetId})
        WITH r, 
             CASE WHEN r.confidence IS NOT NULL THEN r.confidence ELSE 0.5 END as baseConfidence,
             size((a)--()) as aConnections,
             size((b)--()) as bConnections
        RETURN baseConfidence * (1 + log(aConnections + bConnections) / 10) as score
      `, { sourceId, targetId });

      if (result.records.length > 0) {
        return result.records[0].get('score');
      }

      return 0.5;
    } finally {
      await session.close();
    }
  }

  private calculateChainSeverity(path: any): string {
    // Analyze path to determine severity
    const hasVulnerability = path.segments.some((seg: any) => 
      seg.end.labels.includes('VULNERABILITY')
    );
    
    const hasCriticalNode = path.segments.some((seg: any) => 
      seg.end.properties.severity === 'critical'
    );

    if (hasCriticalNode) return 'CRITICAL';
    if (hasVulnerability) return 'HIGH';
    if (path.length > 3) return 'MEDIUM';
    return 'LOW';
  }

  async createGraphProjection(name: string): Promise<void> {
    const session = this.driver.session();
    
    try {
      await session.run(`
        CALL gds.graph.project(
          $name,
          ['IP', 'DOMAIN', 'ASN', 'CERTIFICATE'],
          {
            RESOLVES_TO: { orientation: 'UNDIRECTED' },
            BELONGS_TO: { orientation: 'UNDIRECTED' },
            SHARES_CERT: { orientation: 'UNDIRECTED' }
          }
        )
      `, { name });

      logger.info('Graph projection created', { name });
    } catch (error) {
      logger.error('Failed to create projection', error);
    } finally {
      await session.close();
    }
  }
}
