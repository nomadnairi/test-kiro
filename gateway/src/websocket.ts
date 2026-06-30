import WebSocket from 'ws';
import { FastifyRequest } from 'fastify';
import { createLogger, WSMessageType } from '@cyberintel/shared';
import Redis from 'ioredis';

const logger = createLogger({ service: 'gateway-ws' });

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
const subscriber = redis.duplicate();

const connections = new Map<string, WebSocket>();
const userSubscriptions = new Map<string, Set<string>>();
const userRoles = new Map<string, string>();

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
    if (shouldReceiveMessage(userId, data, channel)) {
      connection.send(JSON.stringify({
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

function shouldReceiveMessage(userId: string, data: any, channel: string): boolean {
  // 1. Direct user targeting
  if (data && data.userId) {
    return data.userId === userId;
  }

  // 2. Global channels
  if (channel === 'system:alerts') {
    return true;
  }

  // 3. Admin access
  const role = userRoles.get(userId);
  if (role === 'admin') {
    return true;
  }

  // 4. Check active subscriptions
  const subs = userSubscriptions.get(userId);
  if (subs && subs.has(channel)) {
    return true;
  }

  return false;
}

export async function wsHandler(connection: WebSocket, request: FastifyRequest) {
  try {
    // Verify JWT from query params
    const token = (request.query as any).token;
    if (!token) {
      connection.close(1008, 'Unauthorized');
      return;
    }

    const decoded = request.server.jwt.verify(token) as any;
    const userId = decoded.id;
    const role = decoded.role || 'analyst';

    connections.set(userId, connection);
    userRoles.set(userId, role);

    // Initialize subscriptions
    if (!userSubscriptions.has(userId)) {
      userSubscriptions.set(userId, new Set<string>());
    }

    logger.info('WebSocket connected', { userId, role });

    connection.on('message', async (message: Buffer) => {
      try {
        const data = JSON.parse(message.toString());
        const subs = userSubscriptions.get(userId)!;
        
        // Handle client messages
        switch (data.type) {
          case 'subscribe':
            if (Array.isArray(data.channels)) {
              data.channels.forEach((ch: string) => subs.add(ch));
              logger.info('Client subscribed', { userId, channels: data.channels });
            }
            break;
          case 'unsubscribe':
            if (Array.isArray(data.channels)) {
              data.channels.forEach((ch: string) => subs.delete(ch));
              logger.info('Client unsubscribed', { userId, channels: data.channels });
            }
            break;
          case 'ping':
            connection.send(JSON.stringify({ type: 'pong' }));
            break;
        }
      } catch (error) {
        logger.error('WebSocket message error', error);
      }
    });

    connection.on('close', () => {
      connections.delete(userId);
      userSubscriptions.delete(userId);
      userRoles.delete(userId);
      logger.info('WebSocket disconnected', { userId });
    });

    connection.on('error', (error: any) => {
      logger.error('WebSocket error', error, { userId });
      connections.delete(userId);
      userSubscriptions.delete(userId);
      userRoles.delete(userId);
    });

  } catch (error) {
    logger.error('WebSocket handler error', error);
    connection.close(1011, 'Internal error');
  }
}
