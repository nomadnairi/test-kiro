import neo4j, { Driver, Session } from 'neo4j-driver';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'graph-service' });

export class GraphService {
  private driver: Driver;

  constructor(driver: Driver) {
    this.driver = driver;
  }

  async createNode(label: string, properties: Record<string, any>): Promise<any> {
    const session = this.driver.session();
    try {
      const result = await session.run(`CREATE (n:${label} $properties) RETURN n`, { properties });
      return result.records[0].get('n').properties;
    } finally {
      await session.close();
    }
  }

  async createRelationship(
    sourceId: string,
    targetId: string,
    type: string,
    properties: Record<string, any> = {}
  ): Promise<any> {
    const session = this.driver.session();
    try {
      const result = await session.run(
        `MATCH (a {id: $sourceId}), (b {id: $targetId})
         CREATE (a)-[r:${type} $properties]->(b)
         RETURN r`,
        { sourceId, targetId, properties }
      );
      return result.records[0].get('r').properties;
    } finally {
      await session.close();
    }
  }

  async query(cypher: string, params: Record<string, any> = {}): Promise<any[]> {
    const session = this.driver.session();
    try {
      const result = await session.run(cypher, params);
      return result.records.map((record) => record.toObject());
    } finally {
      await session.close();
    }
  }

  async getNeighbors(nodeId: string, depth: number = 1): Promise<any> {
    const session = this.driver.session();
    try {
      const result = await session.run(
        `MATCH path = (n {id: $nodeId})-[*1..${depth}]-(m)
         RETURN nodes(path) as nodes, relationships(path) as relationships`,
        { nodeId }
      );

      const nodes = new Map();
      const edges = new Map();

      result.records.forEach((record) => {
        const pathNodes = record.get('nodes');
        const pathRels = record.get('relationships');

        pathNodes.forEach((node: any) => {
          nodes.set(node.identity.toString(), {
            id: node.properties.id,
            label: node.labels[0],
            properties: node.properties,
          });
        });

        pathRels.forEach((rel: any) => {
          edges.set(rel.identity.toString(), {
            id: rel.identity.toString(),
            source: rel.start.toString(),
            target: rel.end.toString(),
            type: rel.type,
            properties: rel.properties,
          });
        });
      });

      return {
        nodes: Array.from(nodes.values()),
        edges: Array.from(edges.values()),
      };
    } finally {
      await session.close();
    }
  }

  async findPaths(sourceId: string, targetId: string, maxDepth: number = 5): Promise<any[]> {
    const session = this.driver.session();
    try {
      const result = await session.run(
        `MATCH path = shortestPath((a {id: $sourceId})-[*..${maxDepth}]-(b {id: $targetId}))
         RETURN path`,
        { sourceId, targetId }
      );

      return result.records.map((record) => {
        const path = record.get('path');
        const segments = path.segments;
        const len = segments.length;
        const nodes = new Array(len);
        const relationships = new Array(len);

        for (let i = 0; i < len; i++) {
          const seg = segments[i];
          nodes[i] = seg.start.properties;
          relationships[i] = {
            type: seg.relationship.type,
            properties: seg.relationship.properties,
          };
        }

        return { nodes, relationships };
      });
    } finally {
      await session.close();
    }
  }
}
