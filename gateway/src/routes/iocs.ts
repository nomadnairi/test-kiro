import { FastifyInstance } from 'fastify';
import { Pool } from 'pg';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'gateway-iocs' });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function iocRoutes(fastify: FastifyInstance) {
  // Get IOC
  fastify.get('/:iocId', async (request, reply) => {
    const { iocId } = request.params as { iocId: string };

    const result = await pool.query(
      'SELECT * FROM iocs WHERE id = $1',
      [iocId]
    );

    if (result.rows.length === 0) {
      return reply.code(404).send({ error: 'IOC not found' });
    }

    return result.rows[0];
  });

  // Search IOCs
  fastify.get('/', async (request, reply) => {
    const { q, type, threatLevel, source, limit = 50, offset = 0 } = request.query as any;

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

    return { iocs: result.rows };
  });

  // Get IOC feed (recent)
  fastify.get('/feed/recent', async (request, reply) => {
    const { limit = 100 } = request.query as any;

    const result = await pool.query(
      `SELECT * FROM iocs
       WHERE last_seen > NOW() - INTERVAL '24 hours'
       ORDER BY last_seen DESC
       LIMIT $1`,
      [limit]
    );

    return { iocs: result.rows };
  });
}
