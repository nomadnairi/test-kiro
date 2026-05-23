import { FastifyError, FastifyRequest, FastifyReply } from 'fastify';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'gateway' });

export async function errorHandler(
  error: FastifyError,
  request: FastifyRequest,
  reply: FastifyReply
) {
  logger.error('Request error', error, {
    url: request.url,
    method: request.method,
    statusCode: error.statusCode,
  });

  const statusCode = error.statusCode || 500;
  const message = statusCode === 500 ? 'Internal Server Error' : error.message;

  reply.code(statusCode).send({
    error: message,
    statusCode,
    timestamp: new Date().toISOString(),
  });
}
