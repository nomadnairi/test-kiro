import { FastifyInstance } from 'fastify';
import { Pool } from 'pg';
import { createLogger, EntityType } from '@cyberintel/shared';
import { z } from 'zod';

const logger = createLogger({ service: 'gateway-entities' });

// Validation schemas
const EntityIdSchema = z.object({
  entityId: z.string().uuid('Invalid entity ID format'),
});

const SearchEntitiesSchema = z.object({
  q: z.string().min(1).max(200).optional(),
  type: z.nativeEnum(EntityType).optional(),
  limit: z.coerce.number().int().min(1).max(100).default(50),
  offset: z.coerce.number().int().min(0).default(0),
});

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function entityRoutes(fastify: FastifyInstance) {
  // Get entity
  fastify.get('/:entityId', async (request, reply) => {
    try {
      const { entityId } = EntityIdSchema.parse(request.params);

      const result = await pool.query('SELECT * FROM entities WHERE id = $1', [entityId]);

      if (result.rows.length === 0) {
        return reply.code(404).send({ error: 'Entity not found' });
      }

      return result.rows[0];
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      logger.error('Get entity failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });

  // Search entities
  fastify.get('/', async (request, reply) => {
    try {
      const { q, type, limit, offset } = SearchEntitiesSchema.parse(request.query);

      let query = 'SELECT * FROM entities WHERE 1=1';
      const params: any[] = [];
      let paramIndex = 1;

      if (q) {
        query += ` AND value ILIKE $${paramIndex}`;
        params.push(`%${q}%`);
        paramIndex++;
      }

      if (type) {
        query += ` AND type = $${paramIndex}`;
        params.push(type);
        paramIndex++;
      }

      query += ` ORDER BY last_seen DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
      params.push(limit, offset);

      const result = await pool.query(query, params);

      return {
        entities: result.rows,
        pagination: {
          limit,
          offset,
          total: result.rowCount || 0,
        },
      };
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      logger.error('Search entities failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });

  // Get entity relationships
  fastify.get('/:entityId/relationships', async (request, reply) => {
    try {
      const { entityId } = EntityIdSchema.parse(request.params);

      const result = await pool.query(
        `SELECT r.*, 
          e1.value as source_value, e1.type as source_type,
          e2.value as target_value, e2.type as target_type
         FROM relationships r
         JOIN entities e1 ON r.source_id = e1.id
         JOIN entities e2 ON r.target_id = e2.id
         WHERE r.source_id = $1 OR r.target_id = $1`,
        [entityId]
      );

      return { relationships: result.rows };
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      logger.error('Get relationships failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });

  // Get entity timeline
  fastify.get('/:entityId/timeline', async (request, reply) => {
    try {
      const { entityId } = EntityIdSchema.parse(request.params);

      const result = await pool.query(
        `SELECT * FROM timeline_events
         WHERE entity_id = $1
         ORDER BY timestamp DESC`,
        [entityId]
      );

      return { events: result.rows };
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      logger.error('Get timeline failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });
}
