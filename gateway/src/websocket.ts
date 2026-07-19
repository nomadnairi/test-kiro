import { SocketStream } from '@fastify/websocket';
import { FastifyRequest } from 'fastify';
import { createLogger, WSMessageType } from '@cyberintel/shared';
import Redis from 'ioredis';

const logger = createLogger({ service: 'gateway-ws' });

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
const subscriber = redis.duplicate();

const connections = new Map<string, SocketStream>();

// Subscribe to Redis channels
subscriber.subscribe(
  'scan:updates',
  'entity:discovered',
  'ioc:detected',
  'task:updates',
  'agent:messages',
  'system:alerts'
);

subscriber.on('message', (channel, message) => {
  const data = JSON.parse(message);
  
  // Broadcast to relevant connections
  connections.forEach((connection, userId) => {
    if (shouldReceiveMessage(userId, data)) {
      connection.socket.send(JSON.stringify({
        type: getMessageType(channel),
        payload: data,
        timestamp: new Date().toISOString(),
      }));
    }
  });
});

function getMessageType(channel: string): WSMessageType {
  const mapping: Record<string, WSMessageType> = {
    'scan:updates': WSMessageType.SCAN_UPDATE,
    'entity:discovered': WSMessageType.ENTITY_DISCOVERED,
    'ioc:detected': WSMessageType.IOC_DETECTED,
    'task:updates': WSMessageType.TASK_UPDATE,
    'agent:messages': WSMessageType.AGENT_MESSAGE,
    'system:alerts': WSMessageType.SYSTEM_ALERT,
  };
  return mapping[channel] || WSMessageType.SYSTEM_ALERT;
}

function shouldReceiveMessage(userId: string, data: any): boolean {
  // TODO: Implement proper filtering based on user permissions and subscriptions
  return true;
}

export async function wsHandler(connection: SocketStream, request: FastifyRequest) {
  try {
    // Verify JWT from query params
    const token = (request.query as any).token;
    if (!token) {
      connection.socket.close(1008, 'Unauthorized');
      return;
    }

    const decoded = request.server.jwt.verify(token) as any;
    const userId = decoded.id;

    connections.set(userId, connection);
    logger.info('WebSocket connected', { userId });

    connection.socket.on('message', async (message: Buffer) => {
      try {
        const data = JSON.parse(message.toString());
        
        // Handle client messages
        switch (data.type) {
          case 'subscribe':
            // Subscribe to specific channels
            logger.info('Client subscribed', { userId, channels: data.channels });
            break;
          case 'unsubscribe':
            // Unsubscribe from channels
            logger.info('Client unsubscribed', { userId, channels: data.channels });
            break;
          case 'ping':
            connection.socket.send(JSON.stringify({ type: 'pong' }));
            break;
        }
      } catch (error) {
        logger.error('WebSocket message error', error);
      }
    });

    connection.socket.on('close', () => {
      connections.delete(userId);
      logger.info('WebSocket disconnected', { userId });
    });

    connection.socket.on('error', (error: Error) => {
      logger.error('WebSocket error', error, { userId });
      connections.delete(userId);
    });

  } catch (error) {
    logger.error('WebSocket handler error', error);
    connection.socket.close(1011, 'Internal error');
  }
}
