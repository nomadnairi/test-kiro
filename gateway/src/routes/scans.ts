import { FastifyInstance } from 'fastify';
import { Pool } from 'pg';
import { z } from 'zod';
import { createLogger, EntityType, ScanStatus } from '@cyberintel/shared';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

const logger = createLogger({ service: 'gateway-scans' });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const CreateScanSchema = z.object({
  target: z.string(),
  targetType: z.nativeEnum(EntityType).optional(),
  modules: z.array(z.string()).optional(),
  depth: z.number().min(1).max(5).optional(),
  autoRecon: z.boolean().optional(),
});

export async function scanRoutes(fastify: FastifyInstance) {
  // Create scan
  fastify.post('/', async (request, reply) => {
    try {
      const user = request.user as any;
      const data = CreateScanSchema.parse(request.body);

      const scanId = uuidv4();

      // Create scan record
      await pool.query(
        `INSERT INTO scans (id, target, target_type, status, progress, user_id, created_at)
         VALUES ($1, $2, $3, $4, $5, $6, NOW())`,
        [scanId, data.target, data.targetType || EntityType.DOMAIN, ScanStatus.PENDING, 0, user.id]
      );

      // Send to orchestrator with timeout and error handling
      try {
        await axios.post(
          `${process.env.ORCHESTRATOR_URL || 'http://localhost:8002'}/api/tasks`,
          {
            scanId,
            target: data.target,
            targetType: data.targetType,
            modules: data.modules,
            depth: data.depth || 2,
            autoRecon: data.autoRecon !== false,
          },
          { timeout: 5000 }
        );
      } catch (orchError) {
        logger.error('Failed to send to orchestrator', orchError);
        // Update scan status to failed
        await pool.query(
          'UPDATE scans SET status = $1, error = $2 WHERE id = $3',
          [ScanStatus.FAILED, 'Failed to start scan', scanId]
        );
        throw new Error('Failed to start scan');
      }

      logger.info('Scan created', { scanId, target: data.target, userId: user.id });

      return { scanId, status: ScanStatus.PENDING };
    } catch (error) {
      logger.error('Failed to create scan', error);
      if (error instanceof z.ZodError) {
        return reply.code(400).send({ error: 'Invalid input', details: error.errors });
      }
      throw error;
    }
  });

  // Get scan
  fastify.get('/:scanId', async (request, reply) => {
    const { scanId } = request.params as { scanId: string };

    const result = await pool.query(
      `SELECT s.*, 
        (SELECT COUNT(*) FROM entities WHERE scan_id = s.id) as entity_count,
        (SELECT COUNT(*) FROM iocs WHERE scan_id = s.id) as ioc_count
       FROM scans s
       WHERE s.id = $1`,
      [scanId]
    );

    if (result.rows.length === 0) {
      return reply.code(404).send({ error: 'Scan not found' });
    }

    return result.rows[0];
  });

  // List scans
  fastify.get('/', async (request, reply) => {
    const user = request.user as any;
    const { limit = 50, offset = 0 } = request.query as any;

    const result = await pool.query(
      `SELECT s.*,
        (SELECT COUNT(*) FROM entities WHERE scan_id = s.id) as entity_count,
        (SELECT COUNT(*) FROM iocs WHERE scan_id = s.id) as ioc_count
       FROM scans s
       WHERE s.user_id = $1
       ORDER BY s.created_at DESC
       LIMIT $2 OFFSET $3`,
      [user.id, limit, offset]
    );

    return { scans: result.rows };
  });

  // Get scan results
  fastify.get('/:scanId/results', async (request, reply) => {
    const { scanId } = request.params as { scanId: string };

    const [scan, entities, iocs, relationships] = await Promise.all([
      pool.query('SELECT * FROM scans WHERE id = $1', [scanId]),
      pool.query('SELECT * FROM entities WHERE scan_id = $1', [scanId]),
      pool.query('SELECT * FROM iocs WHERE scan_id = $1', [scanId]),
      pool.query('SELECT * FROM relationships WHERE scan_id = $1', [scanId]),
    ]);

    if (scan.rows.length === 0) {
      return reply.code(404).send({ error: 'Scan not found' });
    }

    return {
      scan: scan.rows[0],
      entities: entities.rows,
      iocs: iocs.rows,
      relationships: relationships.rows,
    };
  });

  // Cancel scan
  fastify.post('/:scanId/cancel', async (request, reply) => {
    const { scanId } = request.params as { scanId: string };

    await pool.query(
      'UPDATE scans SET status = $1 WHERE id = $2',
      [ScanStatus.CANCELLED, scanId]
    );

    // Notify orchestrator with timeout
    try {
      await axios.post(
        `${process.env.ORCHESTRATOR_URL || 'http://localhost:8002'}/api/tasks/${scanId}/cancel`,
        {},
        { timeout: 5000 }
      );
    } catch (error) {
      logger.warn('Failed to notify orchestrator of cancellation', { scanId, error });
      // Continue anyway - scan is marked as cancelled in DB
    }

    logger.info('Scan cancelled', { scanId });

    return { success: true };
  });
}
