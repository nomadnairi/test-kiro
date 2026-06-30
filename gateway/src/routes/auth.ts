import { FastifyInstance } from 'fastify';
import bcrypt from 'bcrypt';
import { Pool } from 'pg';
import { z } from 'zod';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'gateway-auth' });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const RegisterSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3),
  password: z.string().min(8),
});

export async function authRoutes(fastify: FastifyInstance) {
  // Register
  fastify.post('/register', async (request, reply) => {
    try {
      const { email, username, password } = RegisterSchema.parse(request.body);

      // Check if user exists
      const existing = await pool.query('SELECT id FROM users WHERE email = $1 OR username = $2', [
        email,
        username,
      ]);

      if (existing.rows.length > 0) {
        return reply.code(409).send({ error: 'User already exists' });
      }

      // Hash password
      const passwordHash = await bcrypt.hash(password, 10);

      // Create user
      const result = await pool.query(
        `INSERT INTO users (email, username, password_hash, role, created_at)
         VALUES ($1, $2, $3, $4, NOW())
         RETURNING id, email, username, role, created_at`,
        [email, username, passwordHash, 'analyst']
      );

      const user = result.rows[0];

      // Generate token
      const token = fastify.jwt.sign({
        id: user.id,
        email: user.email,
        role: user.role,
      });

      logger.info('User registered', { userId: user.id, email });

      return { user, token };
    } catch (error) {
      logger.error('Registration failed', error);
      throw error;
    }
  });

  // Login
  fastify.post('/login', async (request, reply) => {
    try {
      const { email, password } = LoginSchema.parse(request.body);

      // Get user
      const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);

      if (result.rows.length === 0) {
        return reply.code(401).send({ error: 'Invalid credentials' });
      }

      const user = result.rows[0];

      // Verify password
      const valid = await bcrypt.compare(password, user.password_hash);
      if (!valid) {
        return reply.code(401).send({ error: 'Invalid credentials' });
      }

      // Update last login
      await pool.query('UPDATE users SET last_login = NOW() WHERE id = $1', [user.id]);

      // Generate token
      const token = fastify.jwt.sign({
        id: user.id,
        email: user.email,
        role: user.role,
      });

      logger.info('User logged in', { userId: user.id, email });

      return {
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          role: user.role,
        },
        token,
      };
    } catch (error) {
      logger.error('Login failed', error);
      throw error;
    }
  });

  // Verify token
  fastify.get('/verify', async (request, reply) => {
    try {
      await request.jwtVerify();
      const user = request.user as any;

      const result = await pool.query('SELECT id, email, username, role FROM users WHERE id = $1', [
        user.id,
      ]);

      if (result.rows.length === 0) {
        return reply.code(401).send({ error: 'User not found' });
      }

      return { user: result.rows[0] };
    } catch (error) {
      return reply.code(401).send({ error: 'Invalid token' });
    }
  });
}
