import { FastifyInstance } from 'fastify';
import { Pool } from 'pg';
import { createLogger, IOCType, ThreatLevel } from '@cyberintel/shared';
import { z } from 'zod';

const logger = createLogger({ service: 'gateway-iocs' });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Validation schemas
const IOCIdSchema = z.object({
  iocId: z.string().uuid('Invalid IOC ID format'),
});

const SearchIOCsSchema = z.object({
  q: z.string().min(1).max(255).optional(),
  type: z.nativeEnum(IOCType).optional(),
  threatLevel: z.nativeEnum(ThreatLevel).optional(),
  source: z.string().min(1).max(100).optional(),
  limit: z.coerce.number().int().min(1).max(100).default(50),
  offset: z.coerce.number().int().min(0).default(0),
});

const RecentFeedSchema = z.object({
  limit: z.coerce.number().int().min(1).max(1000).default(100),
});

export async function iocRoutes(fastify: FastifyInstance) {
  // Get IOC
  fastify.get('/:iocId', async (request, reply) => {
    try {
      const { iocId } = IOCIdSchema.parse(request.params);

      const result = await pool.query('SELECT * FROM iocs WHERE id = $1', [iocId]);

      if (result.rows.length === 0) {
        return reply.code(404).send({ error: 'IOC not found' });
      }

      return result.rows[0];
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      logger.error('Get IOC failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });

  // Search IOCs
  fastify.get('/', async (request, reply) => {
    try {
      const { q, type, threatLevel, source, limit, offset } = SearchIOCsSchema.parse(request.query);

      let query = 'SELECT * FROM iocs WHERE 1=1';
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

      if (threatLevel) {
        query += ` AND threat_level = $${paramIndex}`;
        params.push(threatLevel);
        paramIndex++;
      }

      if (source) {
        query += ` AND source = $${paramIndex}`;
        params.push(source);
        paramIndex++;
      }

      query += ` ORDER BY last_seen DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
      params.push(limit, offset);

      const result = await pool.query(query, params);

      return {
        iocs: result.rows,
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
      logger.error('Search IOCs failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });

  // Get IOC feed (recent)
  fastify.get('/feed/recent', async (request, reply) => {
    try {
      const { limit } = RecentFeedSchema.parse(request.query);

      const result = await pool.query(
        `SELECT * FROM iocs
         WHERE last_seen > NOW() - INTERVAL '24 hours'
         ORDER BY last_seen DESC
         LIMIT $1`,
        [limit]
      );

      return { iocs: result.rows };
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return reply.code(400).send({
          error: 'Validation failed',
          details: error.errors,
        });
      }
      logger.error('Get recent IOCs failed', error);
      return reply.code(500).send({ error: 'Internal server error' });
    }
  });
}
