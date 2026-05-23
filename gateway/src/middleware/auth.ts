import { FastifyRequest, FastifyReply } from 'fastify';

export async function authMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    // Skip auth for public routes
    const publicRoutes = ['/health', '/api/auth/login', '/api/auth/register'];
    if (publicRoutes.some(route => request.url.startsWith(route))) {
      return;
    }

    await request.jwtVerify();
  } catch (err) {
    reply.code(401).send({ error: 'Unauthorized' });
  }
}

export function requireRole(roles: string[]) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    const user = request.user as any;
    
    if (!user || !roles.includes(user.role)) {
      reply.code(403).send({ error: 'Forbidden' });
    }
  };
}
