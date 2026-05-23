import { FastifyInstance } from 'fastify';
import { Pool } from 'pg';
import { createLogger } from '@cyberintel/shared';
import { requireRole } from '../middleware/auth';

const logger = createLogger({ service: 'gateway-users' });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export async function userRoutes(fastify: FastifyInstance) {
  // Get current user
  fastify.get('/me', async (request, reply) => {
    const user = request.user as any;

    const result = await pool.query(
      'SELECT id, email, username, role, created_at, last_login FROM users WHERE id = $1',
      [user.id]
    );

    return result.rows[0];
  });

  // List users (admin only)
  fastify.get('/', {
    preHandler: requireRole(['admin']),
  }, async (request, reply) => {
    const result = await pool.query(
      'SELECT id, email, username, role, created_at, last_login FROM users ORDER BY created_at DESC'
    );

    return { users: result.rows };
  });

  // Get user stats
  fastify.get('/me/stats', async (request, reply) => {
    const user = request.user as any;

    const [scans, entities, iocs] = await Promise.all([
      pool.query('SELECT COUNT(*) FROM scans WHERE user_id = $1', [user.id]),
      pool.query('SELECT COUNT(*) FROM entities WHERE user_id = $1', [user.id]),
      pool.query('SELECT COUNT(*) FROM iocs WHERE user_id = $1', [user.id]),
    ]);

    return {
      totalScans: parseInt(scans.rows[0].count),
      totalEntities: parseInt(entities.rows[0].count),
      totalIOCs: parseInt(iocs.rows[0].count),
    };
  });
}
